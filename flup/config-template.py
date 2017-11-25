import os

_basedir = os.path.abspath(os.path.dirname(__file__))

# APPLICATION ROOT
APPLICATION_ROOT = '/flup'

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
LDAPURI = 'ldap://localhost'
BINDDN = 'cn=admin,dc=example,dc=org'
BINDPW = 'password'
BASEDN = 'dc=garr,dc=it'

# BABEL

SUPPORTED_LANGUAGES = {'it': 'Italian', 'en': 'English'}
BABEL_DEFAULT_LOCALE = 'it'
BABEL_DEFAULT_TIMEZONE = 'Europe/Rome'

# HOSTNAME

IDP_BASE_URL = 'https://idp.example.org'

# MAIL

MAIL_SERVER = 'smtp.example.org'
MAIL_DEFAULT_SENDER = 'noreply@example.org'
MAIL_SIGNATURE = 'MAIL_SIGNATURE'

# ORGNAME
ORGNAME = 'Organization Name'
