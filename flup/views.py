# coding=utf-8
from flup import app, ldapservices, mail_services, db
from flask import render_template, url_for, redirect, flash, abort, request, g
from model import Token, UserMail, User
from forms import LoginForm, NewPasswordForm, EmailForm, ActivationsPUIDForm
from flask_login import login_required, login_user, current_user, logout_user
from flask_babel import gettext


@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    username = form.username.data
    user = None
    if form.validate_on_submit():
        try:
            user = ldapservices.user_login(form.username.data, form.password.data)
        except Exception as e:
            app.logger.error('LDAP Exception: %s', e)
            abort(500)
        if user:
            login_user(user)
            app.logger.info('Login: username %s', username)
            return render_template('user_menu.html', user=user)
        else:
            flash(gettext('Nome utente o password invalide.'), 'error')
            app.logger.info('Login failed: username %s', username)
    return render_template('login.html', form=form)

@app.route('/user_menu')
@login_required
def user_menu():
    user = current_user
    return render_template('user_menu.html', user=user)


def password_is_safe(user, password):
    if (len(password) > 7 and
        user.givenName.lower() not in password.lower() and
        user.sn.lower() not in password.lower()):
        return True
    return False

@app.route('/change_pw', methods=['GET', 'POST'])
@login_required
def change_pw():
    app.logger.debug('change_pw requested')
    error = ''
    form = NewPasswordForm()
    user = current_user
    password = form.password.data
    if form.validate_on_submit():
        if password_is_safe(user, password):
            try:
                r = ldapservices.change_userpw(user, password)
            except Exception as e:
                app.logger.error('LDAP Exception: %s', e)
                abort(500)
            flash(gettext('Password modificata con successo.'), 'message')
            app.logger.info('Password changed: username %s', user.uid)
            return redirect(url_for('user_menu'))
        else:
            error = (
                'Le password non posso contenere il proprio nome o '
                'cognome e devono essere lunghe almeno 8 caratteri.'
            )
            form.password.errors.append(error)
    return render_template('change_pw.html', form=form, error=error)


@app.route('/reset_pw', methods=['GET', 'POST'])
def reset_pw():
    form = EmailForm()
    if form.validate_on_submit():
        email = form.email.data
        user = None
        try:
            user = ldapservices.get_user_by_mail(email)
        except Exception as e:
            app.logger.error('LDAP Exception: %s', e)
            abort(500)
        if user:
            app.logger.info(
                'Password reset requested: username %s, mail %s',
                user.uid,
                email
            )
            if send_mail_op(user, 'IDP Reset password', 'change_pw'):
                flash(gettext('Messaggio di reset inviato.'), 'message')
                app.logger.info(
                    'Password reset sent: username %s, mail %s',
                    user.uid,
                    email
                )
            else:
                flash(gettext('Email non valida.'), 'error')
                app.logger.info(
                    'Password reset failed: mail %s',
                    email
                )
    return render_template('reset_pw.html', form=form)


@app.route('/activation', methods=['GET', 'POST'])
def activation():
    form = ActivationsPUIDForm()
    if form.validate_on_submit():
        spuid = form.spuid.data
        user = None
        try:
            user = ldapservices.get_user_by_attr('schacPersonalUniqueID', spuid)
        except Exception as e:
            app.logger.error('LDAP Exception: %s', e)
            abort(500)
        if user and user.mail:
            login_user(user)
            app.logger.info('Activation request: username %s', user.uid)
            return redirect(url_for('activation_mail'))
        else:
            flash(gettext('Codice non valido.'), 'error')
            app.logger.info(
                'Activation request failed: schacPersonalUniqueID %s',
                user.uid
            )
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
        try:
            db.session.add(user_mail)
            db.session.commit()
        except Exception as e:
            app.logger.error('SQL Exception: %s', e)
        app.logger.info(
            'Activation mail acquired: username %s, mail %s',
            user.uid,
            email
        )
        if send_mail_op(user, 'IDP account activation', 'activate'):
            flash(gettext('Messaggio di attivazione inviato.'), 'message')
        app.logger.info(
            'Activation mail sent: username %s, mail %s',
            user.uid,
            email
        )
    return render_template('activation_mail.html', form=form, user=user)

@app.route('/new_mail', methods=['GET', 'POST'])
@login_required
def new_mail():
    user = current_user
    form = EmailForm()
    if form.validate_on_submit():
        email = form.email.data
        user.mail = email
        user_mail = UserMail(email, user.id)
        try:
            db.session.add(user_mail)
            db.session.commit()
        except Exception as e:
            app.logger.error('SQL Exception: %s', e)
        app.logger.info(
            'New mail acquired: username %s, mail %s',
            user.uid,
            email
        )
        if send_mail_op(user, 'IDP account new mail', 'new_mail'):
            flash(gettext('Messaggio di verifica inviato.'), 'message')
        app.logger.info(
            'Set new_mail mail sent: username %s, mail %s',
            user.uid,
            email
        )
        return redirect(url_for('/user_menu'))
    return render_template('new_mail.html', form=form, user=user)


@app.route('/activate_op', methods=['GET', 'POST'])
@login_required
def activate():
    user = current_user
    app.logger.info('activate_op requested: username %s', user.uid)
    if set_new_mail(user):
        app.logger.info(
            'User activated: username %s',
            user.uid
        )
        return redirect(url_for('change_pw'))
    else:
        app.logger.error(
            'User cannot be activated: username %s',
            user.uid
        )
        abort(500)


@app.route('/logout')
@login_required
def logout():
    user = current_user
    app.logger.info('Logout: username %s', user.uid)
    logout_user()
    return redirect(url_for('index'))


@app.route('/token_op')
def token_op():
    token_value = request.args.get('token')
    op = request.args.get('op')
    app.logger.info(
        'Token Operation: token %s, op %s',
        token_value,
        op
    )

    token = Token.query.filter_by(value=token_value).first()
    user = None
    if token:
        try:
            user = ldapservices.get_user_by_dn(token.user_id)
        except Exception as e:
            app.logger.error('LDAP Exception: %s', e)
            abort(500)
        login_user(user)
        app.logger.info(
            "Token Login: token %s, username %s",
            token_value,
            user.uid
        )
        return redirect(url_for(op))
    else:
        app.logger.info(
            "Token Login failed: token %s",
            token_value
        )
        abort(401)


def send_mail_op(user, subject, op):
    token = Token(user.id)
    db.session.add(token)
    db.session.commit()
    op_url = app.config['IDP_BASE_URL'] + url_for('token_op', token=token.value, op=op)
    body = render_template(
        op + '.j2',
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
        app.logger.error('MAIL Exception: %s', e)
        abort(500)
    return True


def set_new_mail(user):
    user_mail = UserMail.query.filter_by(user_id=user.id).first()
    if user_mail:
        r = None
        try:
            r = ldapservices.change_usermail(user, user_mail.email)
        except Exception as e:
            app.logger.error('LDAP Exception: %s', e)
            abort(500)
        if r:
            return True
    return None
