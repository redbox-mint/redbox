import time
from org.apache.commons.lang import StringEscapeUtils
from java.io import File
from java.util import Date
from java.text import SimpleDateFormat
from com.googlecode.fascinator.common import JsonSimple

class DatasetData:
    def __activate__(self, context):
        self.formData = context["formData"]
        self.Services = context["Services"]
        self.metadata = context["metadata"]
        self.log = context["log"]

    def getFormData(self, field):
        return StringEscapeUtils.escapeHtml(self.formData.get(field, ""))

    def getCurrentTime(self):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ")

    def getCleanId(self, id):
        return id.replace(":","").replace(".","")
    
    def getParkedPayload(self, oid):
        # Get the object from storage
        storage = self.Services.getStorage()
        object = storage.getObject(oid)
        
        # Find the parked payload
        parkedPayload = ""
        pidList = object.getPayloadIdList()
        for pid in pidList:
            if (pid.endswith(".parked")):
                parkedPayload = pid
        object.close()
        return parkedPayload
    
    def getPendingUpdates(self, oid):
        storage = self.Services.getStorage()
        object = storage.getObject(oid)
        indexFile = File(object.getPath() + "/parked_Version_Index.json")
        self.pendingUpdates = []
        self.allUpdates = []
        if indexFile.exists():
            dateFormatter = SimpleDateFormat("yyyyMMddHHmmss")            
            modifiedDate = dateFormatter.parse(object.getMetadata().getProperty("last_modified"))
            parkedVersions = JsonSimple(indexFile).getJsonArray()            
            for version in parkedVersions:
                ts = version.get("timestamp")
                versionDate = dateFormatter.parse(ts)
                self.allUpdates.append(ts)
                if versionDate.after(modifiedDate):
                    self.pendingUpdates.append( ts)
            
        object.close()
        self.pendingUpdateSize = len(self.pendingUpdates)
        self.allUpdateSize = len(self.allUpdates)
        
        return self.pendingUpdates
        
    def formatDate(self, date):
        return self.previewFormatDate(date, "yyyyMMddHHmmss", "yyyy-MM-dd HH:mm:ss")
    
    def getAllUpdates(self):
        return self.allUpdates
    
    def previewFormatDate(self, date, sfmt="yyyy-MM-dd'T'HH:mm:ss", tfmt="dd/MM/yyyy"):    
        dfSource = SimpleDateFormat(sfmt)
        dfTarget = SimpleDateFormat(tfmt)
        return dfTarget.format(dfSource.parse(date))