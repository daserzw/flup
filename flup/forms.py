from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, InputRequired, EqualTo, Email

class NewPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[
        InputRequired(),
        EqualTo('confirm_password', message='Le password devono corrispondere.')
    ])
    confirm_password = PasswordField(
        'Repeat Password', 
        validators=[InputRequired()]
    )

class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[InputRequired()]
    )
    password = PasswordField('Password',
                             validators=[InputRequired()]
    )

class EmailForm(FlaskForm):
    email = StringField('Email',
                          validators=[Email()])

class ActivationsPUIDForm(FlaskForm):
    spuid = StringField('CODICE FISCALE',
                          validators=[InputRequired()])
