# coding=utf-8
from flup import app, ldapservices, mail_services, db
from flask import render_template, url_for, redirect, flash, abort, request, g
from model import Token, UserMail, User
from forms import LoginForm, NewPasswordForm, EmailForm, ActivationsPUIDForm
from flask_login import login_required, login_user, current_user, logout_user
from flask_babel import gettext


@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('user_menu'))
    form = LoginForm()
    username = form.username.data
    if form.validate_on_submit():
        try:
            user = ldapservices.user_login(form.username.data, form.password.data)
        except Exception as e:
            app.logger.error('LDAP Exception: %s', e)
            abort(500)
        if user:
            login_user(user)
            app.logger.warning('Login: username %s', username)
            return redirect(url_for('user_menu'))
        else:
            flash(gettext('Nome utente o password invalide.'), 'error')
            app.logger.warning('Login failed: username %s', username)
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
    message = None
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
            app.logger.warning('Password changed: username %s', user.uid)
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
            app.logger.warning(
                'Password reset requested: username %s, mail %s',
                user.uid,
                email
            )
            if send_mail_op(user, 'IDP - reset password', 'change_pw'):
                flash(gettext('Messaggio di reset inviato.'), 'message')
                app.logger.warning(
                    'Password reset sent: username %s, mail %s',
                    user.uid,
                    email
                )
        else:
            flash(gettext('Email non valida.'), 'error')
            app.logger.warning(
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
        if user:
            if not user.mail:
                login_user(user)
                app.logger.warning('Activation request: username %s', user.uid)
                return redirect(url_for('activation_mail'))
        flash(gettext('Codice Fiscale non valido. Attenzione il codice fiscale deve essere scritto con lettere maiuscole.'), 'error')
        app.logger.warning(
            'Activation request failed: schacPersonalUniqueID %s',
            spuid
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
            abort(500)
        app.logger.warning(
            'Activation mail acquired: username %s, mail %s',
            user.uid,
            email
        )
        if send_mail_op(user, 'IDP - attivazione account', 'activate_op'):
            flash(gettext('Messaggio di attivazione inviato.'), 'message')
            app.logger.warning(
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
            abort(500)
        app.logger.warning(
            'New mail acquired: username %s, mail %s',
            user.uid,
            email
        )
        if send_mail_op(user, 'IDP - nuovo indirizzo mail', 'new_mail_op'):
            flash(gettext('Messaggio di verifica inviato.'), 'message')
        app.logger.warning(
            'Set new_mail mail sent: username %s, mail %s',
            user.uid,
            email
        )
        return redirect(url_for('user_menu'))
    return render_template('new_mail.html', form=form, user=user)

@app.route('/new_mail_op', methods=['GET', 'POST'])
@login_required
def new_mail_op():
    user = current_user
    app.logger.warning('new_mail_op requested: username %s', user.uid)
    if set_new_mail(user):
        app.logger.warning(
            'Set new mail for User: username %s',
            user.uid
        )
        return redirect(url_for('user_menu', message='Indirizzo mail modificato con successo.'))
    else:
        app.logger.error(
            'New mail for user cannot be set: username %s',
            user.uid
        )
        abort(500)


@app.route('/activate_op', methods=['GET', 'POST'])
@login_required
def activate_op():
    user = current_user
    app.logger.warning('activate_op requested: username %s', user.uid)
    email = set_new_mail(user)
    if email:
        user.mail = email
        app.logger.warning(
            'User activated: username %s',
            user.uid
        )
        if send_mail_activated(user):
            return redirect(url_for('change_pw'))
    app.logger.error(
        'User cannot be activated: username %s',
        user.uid
    )
    abort(500)


@app.route('/logout')
@login_required
def logout():
    user = current_user
    app.logger.warning('Logout: username %s', user.uid)
    logout_user()
    return redirect(url_for('index'))


@app.route('/token_op')
def token_op():
    token_value = request.args.get('token')
    op = request.args.get('op')
    app.logger.warning(
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
        app.logger.warning(
            "Token Login: token %s, username %s",
            token_value,
            user.uid
        )
        db.session.delete(token)
        db.session.commit()
        return redirect(url_for(op))
    else:
        app.logger.warning(
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


def send_mail_activated(user):
    user.flupurl = app.config['IDP_BASE_URL']+'/flup'
    body = render_template(
        'activated.j2',
        user=user,
        mail_signature=app.config['MAIL_SIGNATURE']
    )
    try:
        mail_services.send_mail(
            recipients=[user.mail],
            subject='IDP - account attivato',
            body=body
        )
        app.logger.warning(
            'Account activated mail sent: username %s, mail %s',
            user.uid,
            user.mail
        )
    except Exception as e:
        app.logger.error('MAIL Exception: %s', e)
        abort(500)
    return True

def set_new_mail(user):
    user_mail = UserMail.query.filter_by(user_id=user.id).order_by(UserMail.id.desc()).first()
    if user_mail:
        r = None
        try:
            r = ldapservices.change_usermail(user, user_mail.email)
        except Exception as e:
            app.logger.error('LDAP Exception: %s', e)
            abort(500)
        if r:
            db.session.delete(user_mail)
            db.session.commit()
            return user_mail.email
    return None
