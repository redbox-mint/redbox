from com.googlecode.fascinator.common import JsonSimple
from java.lang import Exception,String
from com.googlecode.fascinator.common.storage import StorageUtils
from com.googlecode.fascinator.common import JsonObject
from com.googlecode.fascinator.common import StorageDataUtil
from java.util.regex import Matcher
from java.util.regex import Pattern

class GetmetadataData:
    def __activate__(self, context):
      self.request = context['request']
      self.response = context['response']
      self.services = context['Services']

      self.sessionState = context["sessionState"]
      #Assumption for time being is that users have admin access

      self.storage = self.services.storage
      oid = self.request.getParameter("oid")
      payloadName = self.request.getParameter("payloadName")
      payloadExtension = self.request.getParameter("payloadExtension")
      transformLegacyArrays = self.request.getParameter("transformLegacyArrays")
      jsonObject = None
      if payloadName is not None:
          jsonObject = self.getPayloadJson(oid,payloadName)
      else:
          if payloadExtension is not None:
              jsonObject = self.getPayloadJsonByExtension(oid,payloadExtension)
      if transformLegacyArrays == "true":
          jsonObject = self.transformLegacyArrays(jsonObject)
      writer = self.response.getPrintWriter("application/json; charset=UTF-8")
      writer.println(jsonObject.toString(True))
      writer.close()


    def transformLegacyArrays(self, originalObject):
        outputJsonObject = JsonObject()
        dataUtil = StorageDataUtil()
        outputJsonObject = JsonObject()
        jsonObject = originalObject.getJsonObject()
        for keyString in jsonObject.keySet():
            if self.isAnArrayKey(keyString):
                prefix = self.getPrefix(keyString);
                outputJsonObject.put(prefix, dataUtil.getJavaList(json,prefix));
            else:
                outputJsonObject.put(keyString, jsonObject.get(keyString));
        return JsonSimple(outputJsonObject)

    def getPrefix(self, keyString):
        p = Pattern.compile("(.+)\\.([0-9]+)\\..+")
        m = p.matcher(keyString)
        if m.matches():
            return m.group(1)
        return None

    def isAnArrayKey(self, keyString):
        return keyString.matches(".+\\.[0-9]+\\..+")

    def getObjectMetaJson(self,objectMeta):
        objMetaJson = JsonObject()
        propertyNames = objectMeta.stringPropertyNames()
        for propertyName in propertyNames:
            objMetaJson.put(propertyName,objectMeta.get(propertyName))
        return objMetaJson

    def getObjectMeta(self,oid):
        digitalObject = StorageUtils.getDigitalObject(self.storage, oid)
        return digitalObject.getMetadata()

    def getPayloadJson(self,oid,payloadName):
        digitalObject = StorageUtils.getDigitalObject(self.storage, oid)
        workflowMetaInputStream = digitalObject.getPayload(payloadName).open()
        return JsonSimple(workflowMetaInputStream)

    def getPayloadJsonByExtension(self,oid,payloadExtension):
        digitalObject = StorageUtils.getDigitalObject(self.storage,oid)
        pid = self.findPidForExtenstion(digitalObject, payloadExtension)
        tfPackageInputStream = digitalObject.getPayload(pid).open()
        return JsonSimple(tfPackageInputStream)

    def findPidForExtenstion(self,digitalObject,payloadExtension):
        for pid in digitalObject.getPayloadIdList():
            pidString = String(pid)
            if pidString.endsWith(payloadExtension):
                return pid
        return None
