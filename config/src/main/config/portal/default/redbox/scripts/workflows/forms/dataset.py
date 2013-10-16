import time
from org.apache.commons.lang import StringEscapeUtils

class DatasetData:
    def __activate__(self, context):
        self.formData = context["formData"]
        self.Services = context["Services"]

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
