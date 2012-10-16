class FakeHarvestClient:
    def __init__(self, config = None, input = None, user = "guest"):
        pass
    
    def start(self):
        #print "These tests won't run a real harvest"
        pass
        
    def getUploadOid(self):
        return 123456
    
    def shutdown(self):
        pass
    
class Log:
    def info(self, text):
        print "[INFO]" + text
        
    def error(self, text):
        print "[ERROR]" + text
        
    def debug(self, text):
        print "[DEBUG]" + text