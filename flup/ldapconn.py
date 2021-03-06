import ldap

class Ldapconn():

    # The Borg pattern by Alex Martelli:  "All state is shared, identity is indifferent, you'll be assimilated"!
    
    __shared_state = {} 
    
    def __init__(self, LDAPURI, BINDDN, BINDPW, BASEDN):
        self.__dict__ = self.__shared_state
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
                app.logger.error('LDAPError desc: %s; info: %s' % e.desc, e.info)
        return True
 
    def getLdapobj(self):
        if not self.checkConnection():
            self.connect()
        return self.ldapobj
        
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
                app.logger.error('LDAPError desc: %s; info: %s' % e.desc, e.info)
        return None
        
    def disconnect(self):
       self.ldapobj = None


