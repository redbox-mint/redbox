'''
This is a simple script to demonstrate how to create user lookup hook
'''

def search(user_id):
	print "arg is user_id: %s" % user_id
	if (user_id == '1000'): # if mapping is successful, return real owner
		return "researcher"
	else: # otherwise, assign admin as the owner
		return "admin"        


class UserLookupDemo:
    def __init__(self,url):
    	print "You can initialise it with args %s" % url

    def search(self, user_id):
    	return search(user_id)

if __name__ == "__main__":
    cn = UserLookupLDAPDemo(sys.argv[1])
    uname = cn.search('1000')
    print "User name is: %s" % uname
