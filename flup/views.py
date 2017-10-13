from flup import app, ldapservices, mail_services, db
from flask import render_template, url_for, redirect, session, flash, abort
from model import User
from forms import LoginForm, NewPasswordForm, ResetPasswordEmailForm, ActivationsPUIDForm
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
        else: 
            flash(gettext('Something went wrong...'), 'error') 
    return render_template('change_pw.html', form=form)

@app.route('/reset_pw', methods=['GET', 'POST'])
def reset_pw():
    form = ResetPasswordEmailForm()
    if form.validate_on_submit():
        email = form.email.data
        try:
            user = ldapservices.get_user_by_email(email)
        except Exception as e:
            # TODO: log exception
            print e
            #abort(500)
        body = ''
        if user:
            if send_reset_pw(user):
                flash(gettext('Password reset mail sent!'), 'message') 
    return render_template('reset_pw.html', form=form)


def send_reset_pw(user):
    token = model.Token(user.id)
    db.session.add(token)
    db.session.commit()
    reset_url = app.config['IDP_BASE_URL'] + '/token_auth' + token.value
    body = render_template('reset_password.j2',
                           data={'reset_url':reset_url,
                                 'idp_name':idp_name}
    )
    try:
        mail_services.send_mail(
            recipients=[user.mail],
            subject="password reset",
            body=body
        )
    except Exception as e:
        # TODO: log exception
        print e
        #abort(500)
    return True

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
            return redirect(url_for('activate'))
        else: 
            flash(gettext('Sorry, no user by that code...'), 'error') 
    return render_template('activation.html', form=form)

@app.route('/activate', methods=['GET', 'POST'])
@login_required
def activate():
    user = current_user
    return render_template('activate.html', user=user)
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/send_token', methods=['POST'])
def send_token():
    email = request.get('email')
    if email:
        token = model.Token()
        
@app.route('/token_auth/<token>', methods=['GET'])
def token_auth(token):
    pass
