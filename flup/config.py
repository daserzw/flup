import os

_basedir = os.path.abspath(os.path.dirname(__file__))

# DEBUG
DEBUG = True
TRAP_BAD_REQUEST_ERRORS = True

# DB
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'data/app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True

# SECRET_KEY
SECRET_KEY = 'fdadfetre82302394839u0dsfomdovkn23er124'

# SESSION SECURE COOKIE
#SESSION_COOKIE_SECURE = True


# LDAP
LDAPURI = 'ldap://idp.example.org'
BINDDN = 'cn=admin,dc=example,dc=org'
BINDPW = 'password'
BASEDN = 'dc=example,dc=org'

# BABEL

SUPPORTED_LANGUAGES = {'it': 'Italian', 'en': 'English'}
BABEL_DEFAULT_LOCALE = 'it'
BABEL_DEFAULT_TIMEZONE = 'Europe/Rome'

# HOSTNAME

IDP_BASE_URL = 'https//127.0.0.1:5000'

# MAIL

MAIL_SERVER = 'localhost'
MAIL_DEFAULT_SENDER = 'davide.vaghetti@unipi.it'
MAIL_SIGNATURE = 'MAIL_SIGNATURE'

