from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config.from_object('flup.config')
app.secret_key = app.config['SECRET_KEY']
db = SQLAlchemy(app)
mail = Mail(app)

from flup import views
