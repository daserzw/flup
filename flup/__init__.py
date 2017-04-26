from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config.from_object('flup.config')
app.config.from_envvar('FLUP_SETTINGS')
app.secret_key = app.config['SECRET_KEY']
db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)


from flup import views
