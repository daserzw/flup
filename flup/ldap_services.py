import ldap
from flup import app

class Ldapconn():

    # The Borg pattern by Alex Martelli:  "All state is shared, identity is indifferent, you'll be assimilated"!
    # The Two Borgs pattern by Davide Vaghetti: "All state is shared, identity is True or False, you'll be assimilated"!
    
    __provider_shared_state = {} 
    __consumer_shared_state = {}
    PROVIDER = True
    CONSUMER = False
    
    def __init__(self, LDAPURI, BINDDN, BINDPW, BASEDN, is_a_provider=True):
        if is_a_provider:
            self.__dict__ = self.__provider_shared_state
        else:
            self.__dict__ = self.__consumer_shared_state
        self.LDAPURI = LDAPURI
        self.BINDDN = BINDDN
        self.BINDPW = BINDPW
        self.BASEDN = BASEDN
        self.ldapobj = None

    def connect(self):
        try:
            self.ldapobj = ldap.initialize(self.LDAPURI)
            self.ldapobj.bind_s(self.BINDDN, self.BINDPW, ldap.AUTH_SIMPLE)
        except Exception as e:
            if e == ldap.LDAPError:
                pass
#                app.logger.error('LDAPError desc: %s; info: %s' % e.desc, e.info)
 
    def getLdapconn(self):
        if self.ldapobj == None:
            self.connect()
        if not self.checkConnection():
            self.connect()
        if self.checkConnection():
            return self.ldapobj
        return None
        
    def checkConnection(self):
        if self.ldapobj == None:
            return None
        try:
            search_result = self.ldapobj.search_s(
                self.BASEDN, 
                ldap.SCOPE_BASE,
                '(objectClass=*)'
                )
            if search_result:
                return True
            else:
                return None
        except Exception as e:
            if e == ldap.LDAPError:
                pass
        return None
        
        
    def disconnect(self):
        self.ldapobj = None

    
## Methods for user login, user search, and password modify

def ldap_login(username, password):
    ldapconn = Ldapconn(
        app.config['LDAPURI'],
        app.config['BINDDN'],
        app.config['BINDPW'],
        app.config['BASEDN']
    )
    ldapobj = ldapconn.getLdapconn()
    search_result = ldapobj.search_s(
        ldapconn.BASEDN,
        ldap.SCOPE_SUBTREE,
        '(uid=%s)' % username
    )
    if search_result:
        (user_dn, ldapentry) = search_result[0]
        try:
            user_ldapconn = Ldapconn(
                app.config['LDAPURI'],
                user_dn,
                password,
                app.config['BASEDN']
            )
            return user_dn
        except ldap.INVALID_CREDENTIALS:
            return None
    return None

