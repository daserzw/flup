import ldap
from model import User

class Ldapservice():

    def __init__(self, get_ldapobj_f, LDAPURI, BASEDN):
        self.get_ldapobj_f = get_ldapobj_f
        self.BASEDN = BASEDN
        self.LDAPURI = LDAPURI

    def getLdapobj(self):
        return self.get_ldapobj_f()

    def setLdapobj(self, ldapobj):
        self.ldapobj = ldapobj

    def get_user_by_dn(self, userdn):
        ldapobj = self.getLdapobj()
        search_results = ldapobj.search_s(
            userdn,
            ldap.SCOPE_SUBTREE,
            '(objectClass=*)'
        )
        if search_results:
            return self._load_user(search_results[0])
        return None

    def get_user_by_attr(self, attr, value, exact=False):
        ldapobj = self.getLdapobj()
        wildcard = '*'
        if exact:
            wildcard = ''
        search_results = ldapobj.search_s(
            self.BASEDN,
            ldap.SCOPE_SUBTREE,
            '(%s=%s%s%s)' % (attr, wildcard, value, wildcard)
        )
        if search_results:
            return self._load_user(search_results[0])
        return None
    
    def get_user_by_uid(self, username):
        ldapobj = self.getLdapobj()
        search_results = ldapobj.search_s(
            self.BASEDN,
            ldap.SCOPE_SUBTREE,
            '(uid=%s)' % username
        )
        if search_results:
            return self._load_user(search_results[0])
        return None

    def get_user_by_email(self, email):
        ldapobj = self.getLdapobj()
        search_results = ldapobj.search_s(
            self.BASEDN,
            ldap.SCOPE_SUBTREE,
            '(mail=%s)' % email
        )
        if search_results:
            return self._load_user(search_results[0])
        return None

    def _load_user(self, search_result):
        (userdn, ldapentry) = search_result
        mail = None
        if 'mail' in ldapentry:
            mail = ldapentry['mail'][0]
        return User(userdn, 
                    ' '.join(ldapentry['givenName']),
                    ' '.join(ldapentry['sn']),
                    mail
        )
        
    def user_login(self, username, password):
        user = self.get_user_by_uid(username)
        if user:
            if self.user_bind(user.id, password):
                return user
        return None

    def get_userdn(self, username):
        ldapobj = self.getLdapobj()
        search_result = ldapobj.search_s(
            self.BASEDN,
            ldap.SCOPE_SUBTREE,
            '(uid=%s)' % username
        )
        if search_result:
            (userdn, ldapentry) = search_result[0]
            return userdn
        return None
                
    def change_userpw(self, user, newpw):
        ldapobj = self.getLdapobj()
        ldapobj.passwd_s(user.id, None, newpw)

    def user_bind(self, userdn, password):
        user_ldapobj = ldap.initialize(self.LDAPURI)
        try:
            user_ldapobj.bind_s(userdn, password, ldap.AUTH_SIMPLE)
        except ldap.INVALID_CREDENTIALS:
            return None
        finally:
            user_ldapobj = None
        return True
