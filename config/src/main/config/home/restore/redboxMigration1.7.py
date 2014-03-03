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
    
    def __init__(self):
        self.packagePidSuffix = ".tfpackage"
        self.redboxVersion = None    
    
    def __activate__(self, bindings):
        # Prepare variables
        self.systemConfig = bindings["systemConfig"]
        self.object       = bindings["object"]
        self.log          = bindings["log"]
        self.audit        = bindings["auditMessages"]
        self.pidList      = None

        # Look at some data
        self.oid = self.object.getId()
        
        try:
            # check if object creation and modification dates...
            self.insertCreateAndModifiedDate()
            
            # load the package data..
            self.__getPackageData()
            
            # update the redbox version...
            self.updateVersion()
            
            # save the package data...
            self.__savePackageData()
            
            self.object.close()
        except Exception, e:
            self.object = None
    
    def insertCreateAndModifiedDate(self):
        #check if object created and modified date exists, populate with current date if not..
        propMetadata = self.object.getMetadata()            
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime())
        if (propMetadata.getProperty("date_object_created") is None):                                    
            propMetadata.setProperty("date_object_created", now)
        if (propMetadata.getProperty("date_object_modified") is None):                                
            propMetadata.setProperty("date_object_modified", now)

    def updateVersion(self):
        if self.redboxVersion is None:
            self.redboxVersion = self.systemConfig.getString(None, ["redbox.version.string"])
        if self.redboxVersion is None:
            self.log.error("Error, could not determine system version!")
            return
        self.packageData.getJsonObject().put("redbox:formVersion", self.redboxVersion)
        
    def __getPackageData(self):
        # Find our package payload
        self.packagePid = None
        try:
            self.pidList = self.object.getPayloadIdList()
            for pid in self.pidList:
                if pid.endswith(self.packagePidSuffix):
                    self.packagePid = pid
        except StorageException:
            self.log.error("Error accessing object PID list for object '{}' ", self.oid)
            return
        if self.packagePid is None:
            self.log.debug("Object '{}' has no package data", self.oid)
            return

        # Retrieve our package data
        self.packageData = None
        try:
            payload = self.object.getPayload(self.packagePid)
            try:
                self.packageData = JsonSimple(payload.open())
            except Exception:
                self.log.error("Error parsing JSON '{}'", self.packagePid)
            finally:
                payload.close()
        except StorageException:
            self.log.error("Error accessing '{}'", self.packagePid)
            return
        
    def __savePackageData(self):
        jsonString = String(self.packageData.toString(True))
        inStream = ByteArrayInputStream(jsonString.getBytes("UTF-8"))
        try:
            self.object.updatePayload(self.packagePid, inStream)
        except StorageException, e:
            self.log.error("Error updating package data payload: ", e)  
      