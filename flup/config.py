import os

_basedir = os.path.abspath(os.path.dirname(__file__))

# DEBUG
DEBUG = True
TRAP_BAD_REQUEST_ERRORS = True

# DB
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'data/app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True

# SECRET_KEY
SECRET_KEY = 'bMOB7eu7oGm2tqVujB1F5oXk9v+/12e9WEjaLt3Gpt8='

# SESSION SECURE COOKIE
SESSION_COOKIE_SECURE = True

# LDAP
LDAPURI = 'ldap://'
BINDDN = 'cn=admin,dc=irccs,dc=it'
BINDPW = 'ciaoldap'
BASEDN = 'dc=irccs,dc=it'
