#See also http://code.activestate.com/recipes/230342-use-jython-to-access-an-ldap-server/
#See also http://docs.oracle.com/javase/tutorial/jndi/ops/index.html

from java.util import Hashtable
from javax.naming import Context
from javax.naming.directory import InitialDirContext, SearchControls

class LDAP:
    def __init__(self,url):
        env = Hashtable()
        env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.ldap.LdapCtxFactory")
        env.put(Context.SECURITY_AUTHENTICATION, "none")
        env.put(Context.PROVIDER_URL, url)
        ctx = InitialDirContext(env)
        self.ctx = ctx

    def search(self, criteria, objectclass, returnField, default="admin"):
        srch = SearchControls()
        srch.setSearchScope(SearchControls.SUBTREE_SCOPE)
        srch.setCountLimit(1)
        srch.setReturningAttributes([returnField])
        results = self.ctx.search("", "(&(%s) (objectClass=%s))" % (criteria, objectclass), srch)
        for result in results:
            retval = result.getAttributes().get(returnField).get(0)
            results.close()
            return retval
        else:
            return default
                
print "Searching"
cn = LDAP("ldap://ldap.qut.edu.au:389")
print cn.search("mail=d.dickinson@qut.edu.au", "user", "uid")
print "Done"