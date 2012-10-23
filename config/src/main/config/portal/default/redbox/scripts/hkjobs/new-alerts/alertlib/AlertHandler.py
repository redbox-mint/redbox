import os
from com.googlecode.fascinator.common import JsonObject

class AlertHandler(object):
    """Base handler class for alerts 
    """
    def __init__(self, file, config, baseline):
        """
        Keyword arguments:
        file -- The data file being read
        config -- A com.googlecode.fascinator.common.JsonSimple instance with configuration items
        baseline -- An object containing a base set of data for the alert
        
        """
        self.file = file
        if not os.path.exists(self.file):
            raise AlertException("Requested input file %s does not exist." % self.file)
        self.config = config
        self.baseline = baseline
            
        
    def process(self):
        jsonList = []
        return jsonList
    
    def getNewJsonObject(self):
        return JsonObject(self.baseline)
    
    def getNewJsonObjectDict(self, datadict):
        dict(self.baseline.items() + datadict.items())
    
