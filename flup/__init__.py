import click
from flask import Flask, g, render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from flup.ldapconn import Ldapconn
import logging

log_formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s [%(pathname)s:%(lineno)d]: %(message)s'
)
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
for handler in app.logger.handlers:
    handler.setFormatter(log_formatter)

from flup.ldap_services import Ldapservice

ldapservices = Ldapservice(ldapconn.getLdapobj,
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
    return ldapservices.get_user_by_dn(id)

@app.errorhandler(401)
def page_not_found(e):
    return render_template('401.html'), 401

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Not triggered when DEBUG=True
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

from flup import views
db.create_all()

@app.cli.command()
def create_db():
    click.echo('Create the DB (None if the DB already exists.)')
    db.create_all()

@app.cli.command()    
def recreate_db():
    click.echo('Drop the current DB and recreate it')
    db.drop_all()
    db.create_all()
