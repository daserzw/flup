import ldap
from flup.model import User
from flup import app

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

    def get_user_by_mail(self, mail):
        ldapobj = self.getLdapobj()
        search_results = ldapobj.search_s(
            self.BASEDN,
            ldap.SCOPE_SUBTREE,
            '(mail=%s)' % mail
        )
        if search_results:
            return self._load_user(search_results[0])
        return None

    def _load_user(self, search_result):
        (userdn, ldapentry) = search_result
        is_activated = False
        mail = None
        if 'mail' in ldapentry:
            mail = ldapentry['mail'][0].decode('utf-8')
        if 'userPassword' in ldapentry:
            is_activated = True
        app.logger.debug("userdn: %s\nldapentry: %s" % (userdn,ldapentry))
        user = User(id=userdn,
                    uid=ldapentry['uid'][0].decode('utf-8'),
                    givenName=ldapentry['givenName'][0].decode('utf-8'),
                    sn=ldapentry['sn'][0].decode('utf-8'),
                    mail=mail,
                    is_activated=is_activated
        )
        app.logger.debug("returned user: %s", user)
        return user
    
        
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
        return True
        
    def change_usermail(self, user, newmail):
        ldapobj = self.getLdapobj()
        mod_attrs = [(ldap.MOD_DELETE, 'mail', None)]
        try:
            ldapobj.modify_s(user.id, mod_attrs)
        except Exception as e:
            if e == ldap.NO_SUCH_ATTRIBUTE:
                pass
        mod_attrs = [(ldap.MOD_ADD, 'mail', [newmail.encode('utf-8')])]
        ldapobj.modify_s(user.id, mod_attrs)
        return True
        
    def user_bind(self, userdn, password):
        user_ldapobj = ldap.initialize(self.LDAPURI, bytes_mode=False)
        try:
            user_ldapobj.bind_s(userdn, password, ldap.AUTH_SIMPLE)
        except ldap.INVALID_CREDENTIALS:
            return None
        finally:
            user_ldapobj = None
        return True
