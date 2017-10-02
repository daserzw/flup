from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, InputRequired, EqualTo, Email

class NewPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[
        InputRequired(),
        EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField(
        'Repeat Password', 
        validators=[InputRequired()]
    )

class LoginForm(FlaskForm):
    username = StringField('username', 
                           validators=[InputRequired()]
    )
    password = PasswordField('password', 
                             validators=[InputRequired()]
    )

class ResetPasswordEmailForm(FlaskForm):
    email = PasswordField('Email',
                          validators=[InputRequired()])

