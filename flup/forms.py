from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, InputRequired, EqualTo

class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[
        InputRequired(),
        EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField(
        'Repeat Password', 
        validators=[DataRequired()]
    )

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[InputRequired()])
