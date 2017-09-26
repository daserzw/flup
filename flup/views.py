from flup import app, ldapservice
from flask import render_template, url_for, redirect, session, flash
from model import User
from forms import LoginForm, NewPasswordForm
from flask_login import login_required, login_user, current_user, logout_user

@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        user = ldapservice.user_login(form.username.data, form.password.data)
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
        r = ldapservice.change_userpw(user, password)
        if r:
            flash(gettext('Password changed successfully!'), 'message') 
        else: 
            flash(gettext('Something went wrong...'), 'error') 
    return render_template('change_pw.html', form=form)

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



