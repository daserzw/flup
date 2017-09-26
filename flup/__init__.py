from flask import Flask, g
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from ldapconn import Ldapconn

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config.from_object('flup.config')
#app.config.from_envvar('FLUP_SETTINGS')
app.secret_key = app.config['SECRET_KEY']
babel = Babel(app)
db = SQLAlchemy(app)
mail = Mail(app)
ldapconn = Ldapconn(
    app.config['LDAPURI'],
    app.config['BINDDN'],
    app.config['BINDPW'],
    app.config['BASEDN']
)

from ldapservice import Ldapservice

ldapservice = Ldapservice(ldapconn.getLdapobj,
                          app.config['LDAPURI'],
                          app.config['BASEDN']
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "index"

@babel.localeselector
def get_locale():
    return g.get('lang_code', app.config['BABEL_DEFAULT_LOCALE'])

@login_manager.user_loader
def load_user(id):
    return ldapservice.get_user_by_dn(id)
from flup import views

