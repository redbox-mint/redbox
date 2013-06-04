#This is really just a stub script - you should prepare a local look-up script

class UserLookup:
    def __init__(self):
        pass

    def search(self, data = "admin"):
        return data


if __name__ == "__main__":
    ul = UserLookup()
    uname = ul.search()
    print "User name is: %s" % uname