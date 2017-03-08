from flup import db

class User():

    def __init__(self, userdn):
        self.userdn = userdn

    def get_id(self):
        return userdn

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

