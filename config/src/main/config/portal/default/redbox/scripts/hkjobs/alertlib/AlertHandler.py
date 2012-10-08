import os

class AlertHandler(object):
    """Base handler class for alerts 
    """
    def __init__(self, file, config):
        """
        Keyword arguments:
        file -- The data file being read
        config -- A com.googlecode.fascinator.common.JsonSimple instance with configuration items
        
        """
        self.file = file
        if not os.path.exists(self.file):
            raise AlertException("Requested input file %s does not exist." % self.file)
        self.config = config
            
        
    def process(self):
        jsonList = []
        return jsonList
    
