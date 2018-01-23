import uuid
from flup import db
from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, id, uid, givenName, sn, mail,is_activated=False):
        self.id = id
        self.uid = uid
        self.givenName = givenName
        self.sn = sn
        self.mail = mail
        self.is_activated = is_activated

    def __str__(self):
        return ("id: %s, uid:%s, givenName: %s, sn: %s, mail: %s") % (
            self.id,
            self.uid,
            self.givenName,
            self.sn,
            self.mail,
            self.is_activated
        )


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
