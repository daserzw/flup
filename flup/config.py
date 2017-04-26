import os

_basedir = os.path.abspath(os.path.dirname(__file__))

# DEBUG
DEBUG = True
TRAP_BAD_REQUEST_ERRORS = True

# DB
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'data/app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True

# SECRET_KEY
SECRET_KEY = 'a secret key'

# SESSION SECURE COOKIE
SESSION_COOKIE_SECURE = True

# LDAP
LDAPURI = ''
BINDDN = ''
BINDPW = ''
BASEDN = ''
