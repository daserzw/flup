import uuid
from flup import db
from flask_login import UserMixin

class User(UserMixin):

    def __init__(self, id, uid, givenName, sn, mail):
        self.id = id
        self.uid = uid
        self.givenName = givenName
        self.sn = sn
        self.mail = mail

class Token(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    value = db.Column(db.String(36))
    user_id = db.Column(db.String(255))
    
    def __init__(self, user_id):
        self.value = str(uuid.uuid4())
        self.user_id = user_id

    def __repr__(self):
        return self.value

class UserMail(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(254))
    user_id = db.Column(db.String(255))

    def __init__(self, email, user_id):
        self.email = email
        self.user_id = user_id

    def __repr__(self):
        return (self.email, self.user_id)
