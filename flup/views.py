from flup import app, ldapservices, mail_services, db
from flask import render_template, url_for, redirect, session, flash, abort, request
from model import User, Token, UserMail
from forms import LoginForm, NewPasswordForm, EmailForm, ActivationsPUIDForm
from flask_login import login_required, login_user, current_user, logout_user
from flask_babel import gettext

@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = ldapservices.user_login(form.username.data, form.password.data)
        except Exception as e:
            # TODO: log exception
            print e
            # abort(500)
        if user:
            login_user(user)
            flash(gettext('You have successfully logged in'), 'message')
            return redirect(url_for('change_pw'))
        else:
            flash(gettext('Invalid username or password'), 'error')
    return render_template('login.html', form=form)

@app.route('/change_pw', methods=['GET', 'POST'])
@login_required
def change_pw():
    next_url = request.args.get('next_url')
    form = NewPasswordForm()
    if form.validate_on_submit():
        user = current_user
        password = form.password.data
        try:
            r = ldapservices.change_userpw(user, password)
        except Exception as e:
            # TODO: log exception
            print e
            #abort(500)
        if r:
            flash(gettext('Password changed successfully!'), 'message')
            if next_url:
                return render_template(url_for(next_url))
        else: 
            flash(gettext('Something went wrong...'), 'error') 
    return render_template('change_pw.html', form=form)


@app.route('/reset_pw', methods=['GET', 'POST'])
def reset_pw():
    form = EmailForm()
    if form.validate_on_submit():
        email = form.email.data
        try:
            user = ldapservices.get_user_by_mail(email)
        except Exception as e:
            # TODO: log exception
            print e
            #abort(500)
        body = ''
        if user:
            if send_mail_op(user, 'IDP Reset password' , 'change_pw'):
                flash(gettext('Password reset mail sent!'), 'message')
        else:
            flash(gettext('Sorry, no user by that mail, try again.'), 'error')
    return render_template('reset_pw.html', form=form)

@app.route('/activation', methods=['GET', 'POST'])
def activation():
    form = ActivationsPUIDForm()
    if form.validate_on_submit():
        spuid = form.spuid.data
        user = None
        #        try:
        user = ldapservices.get_user_by_attr('schacPersonalUniqueID', spuid)
        #        except Exception as e:
        # TODO: log exception
        #    print e
        #abort(500)
        if user:
            login_user(user)
            return redirect(url_for('activation_mail'))
        else: 
            flash(gettext('Sorry, no user by that code...'), 'error') 
    return render_template('activation.html', form=form)

@app.route('/activation_mail', methods=['GET', 'POST'])
@login_required
def activation_mail():
    user = current_user
    form = EmailForm()
    if form.validate_on_submit():
        email = form.email.data
        user.mail = email
        user_mail = UserMail(email, user.id)
        db.session.add(user_mail)
        db.session.commit()
        if send_mail_op(user, 'IDP account activation', 'activate'):
            flash(gettext('Activation mail sent!'), 'message') 
    return render_template('activation_mail.html', form=form, user=user)

@app.route('/activate', methods=['GET', 'POST'])
@login_required
def activate():
    user = current_user
    if set_new_mail(user):
        return render_template('activate.html', user=user)
    else:
        abort(500)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/token_op')
def token_op():
    token_value = request.args.get('token')
    op = request.args.get('op')
    token = Token.query.filter_by(value=token_value).first()
    if token:
        user = ldapservices.get_user_by_dn(token.user_id)
        login_user(user)
        return redirect(url_for(op))
    else:
        abort(401)

def send_mail_op(user, subject, op):
    token = Token(user.id)
    db.session.add(token)
    db.session.commit()
    op_url = app.config['IDP_BASE_URL'] + url_for('token_op', token=token.value, op=op)
    body = render_template(
        op+'.j2',
        op_url=op_url,
        mail_signature=app.config['MAIL_SIGNATURE']
    )
    try:
        mail_services.send_mail(
            recipients=[user.mail],
            subject=subject,
            body=body
        )
    except Exception as e:
        # TODO: log exception
        print e
        #abort(500)
    return True

def set_new_mail(user):
    user_mail = UserMail.query.filter_by(user_id=user.id).first()
    if user_mail:
        r = None
        r = ldapservices.change_usermail(user, user_mail.email)
        '''
        try:
            r = ldapservices.change_usermail(user, user_mail.email)
        except Exception as e:
            # TODO: log exception
            print e
            #abort(500)
        '''
        if r: 
            return True
    return None

