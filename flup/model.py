import uuid
from flup import db
from flask_login import UserMixin

class User(UserMixin):

    def __init__(self, id, givenName, sn, mail):
        self.id = id
        self.givenName = givenName
        self.sn = sn
        self.mail = mail

class Token(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    value = db.Column(db.String(36))
    user_id = db.Column(db.String(255))
    operation = db.Column(db.Integer)
    
    def __init__(self, user_id):
        self.value = str(uuid.uuid(4))
        self.user_id = user_id

    def __repr__(self):
        return self.value
