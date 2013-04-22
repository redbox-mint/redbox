class ScriptHandler(object):
    """Base handler class for all script alerts
    """
    def __init__(self, config, baseline):
        """
        Keyword arguments:
        config -- A com.googlecode.fascinator.common.JsonSimple instance with configuration items
        baseline -- An object containing a base set of data for the alert        
        """
        self.config = config
        self.baseline = baseline
        
        
        
    def process(self, data):
        """
        Keyword arguments:
        data -- a single entry from the alert (e.g. a CSV row)
        """
        return 0