import re
import sys
import traceback
import time

from com.googlecode.fascinator.api.storage import StorageException
from com.googlecode.fascinator.common import JsonSimple

from java.io import ByteArrayInputStream
from java.lang import Exception
from java.lang import String

class MigrateData:    
    
    def __activate__(self, bindings):
        # Prepare variables
        self.systemConfig = bindings["systemConfig"]
        self.object       = bindings["object"]
        self.log          = bindings["log"]
        self.audit        = bindings["auditMessages"]
        self.pidList      = None

        # Look at some data
        self.oid = self.object.getId()
        self.log.debug("------------------------------------------------")
        try:
            #check if object created and modified date exists, populate with current date if not..
            propMetadata = self.object.getMetadata()            
            now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime())
            if (propMetadata.getProperty("date_object_created") is None):                                    
                propMetadata.setProperty("date_object_created", now)
            if (propMetadata.getProperty("date_object_modified") is None):                                
                propMetadata.setProperty("date_object_modified", now)
            self.object.close()
        except Exception, e:
            self.object = None

      
      