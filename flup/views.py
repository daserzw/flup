from flup import app
from model import User
from flask import render_template, url_for, redirect
from ldap_services import ldap_login
from forms import LoginForm, PasswordForm


@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    #    if form.validate_on_submit():
    userdn = ldap_login(form.username.data, form.password.data)
    if userdn:
        user = User(userdn)
        login_user(user)
        return redirect(url_for('change_pw'))
    return render_template('index.html', form=form)

@app.route('/change_pw', methods = ['POST'])
def change_pw():
    form = PasswordForm()
    
