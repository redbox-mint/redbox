#See also http://code.activestate.com/recipes/230342-use-jython-to-access-an-ldap-server/
#See also http://docs.oracle.com/javase/tutorial/jndi/ops/index.html

from java.util import Hashtable
from javax.naming import Context
from javax.naming.directory import InitialDirContext, SearchControls
import sys

class UserLookupLDAP:
    def __init__(self,url):
        env = Hashtable()
        env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.ldap.LdapCtxFactory")
        env.put(Context.SECURITY_AUTHENTICATION, "none")
        env.put(Context.PROVIDER_URL, url)
        ctx = InitialDirContext(env)
        self.ctx = ctx

    def search(self, criteria,  returnField, default="guest"):
        srch = SearchControls()
        srch.setSearchScope(SearchControls.SUBTREE_SCOPE)
        srch.setCountLimit(1)
        srch.setReturningAttributes([returnField])
        results = self.ctx.search("", criteria, srch)
        for result in results:
            retval = result.getAttributes().get(returnField).get(0)
            results.close()
            return retval
        else:
            return default

if __name__ == "__main__":
    ##Run with jython UserLookupLDAP.py  
    ## e.g. jython UserLookupLDAP.py ldap://ldap.qut.edu.au:389 mail=d.dickinson@qut.edu.au user uid
    #cn = UserLookupLDAP("ldap://ldap.qut.edu.au:389")
    #print cn.search("(&(mail=d.dickinson@qut.edu.au) (objectClass=user))", "uid")
    cn = UserLookupLDAP(sys.argv[1])
    uname = cn.search("(&(%s) (objectClass=%s))" % (sys.argv[2], sys.argv[3]), sys.argv[4])
    print "User name is: %s" % uname

