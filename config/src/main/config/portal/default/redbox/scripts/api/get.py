from com.googlecode.fascinator.common import JsonSimple
from java.lang import Exception,String
from com.googlecode.fascinator.common.storage import StorageUtils
from com.googlecode.fascinator.common import JsonObject

class GetData:
    def __activate__(self, context):
      self.request = context['request']
      self.response = context['response']
      self.services = context['Services']
      
      self.sessionState = context["sessionState"]
      #Assumption for time being is that users have admin access
      try:
          self.sessionState.set("username", "admin")
          self.storage = self.services.storage
          oid = self.request.getParameter("oid")
          tfPackage = self.getTfPackage(oid, self.getTFPackagePid(oid))
          objectMeta = self.getObjectMeta(oid)
          workflowMeta = self.getWorkflowMeta(oid)
          jsonObject = JsonObject()
          jsonObject.put("tfPackage", tfPackage.getJsonObject())
          jsonObject.put("workflow.metadata", workflowMeta.getJsonObject())
          jsonObject.put("TF-OBJ-META", self.getObjectMetaJson(objectMeta))
          writer = self.response.getPrintWriter("application/json; charset=UTF-8")
          writer.println(JsonSimple(jsonObject).toString(True))
          writer.close()
      finally:
          self.sessionState.remove("username")
      
    def getObjectMetaJson(self,objectMeta):
        objMetaJson = JsonObject()
        propertyNames = objectMeta.stringPropertyNames()
        for propertyName in propertyNames:
            objMetaJson.put(propertyName,objectMeta.get(propertyName))
        return objMetaJson
    
    def getObjectMeta(self,oid):
        digitalObject = StorageUtils.getDigitalObject(self.storage, oid)
        return digitalObject.getMetadata()
    
    def getWorkflowMeta(self,oid):
        digitalObject = StorageUtils.getDigitalObject(self.storage, oid)
        workflowMetaInputStream = digitalObject.getPayload("workflow.metadata").open()
        return JsonSimple(workflowMetaInputStream)
            
    def getTfPackage(self,oid, pid):
        digitalObject = StorageUtils.getDigitalObject(self.storage, oid)
        tfPackageInputStream = digitalObject.getPayload(pid).open()
        return JsonSimple(tfPackageInputStream)
    
    def getTFPackagePid(self,oid):
        digitalObject = StorageUtils.getDigitalObject(self.storage,oid)
        for pid in digitalObject.getPayloadIdList():
            pidString = String(pid)
            if pidString.endsWith("tfpackage"):
                return pid
        return None 
