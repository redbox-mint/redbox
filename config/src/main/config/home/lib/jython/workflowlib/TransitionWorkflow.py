from com.googlecode.fascinator import HarvestClient
from com.googlecode.fascinator.api.storage import PayloadType, StorageException
from com.googlecode.fascinator.common import FascinatorHome, JsonSimpleConfig, \
    JsonObject, JsonSimple
from com.googlecode.fascinator.common.messaging import MessagingServices
from com.googlecode.fascinator.common.storage import StorageUtils
from com.googlecode.fascinator.messaging import TransactionManagerQueueConsumer
from java.io import File, FileInputStream, InputStreamReader
from java.lang import Exception
from java.util import LinkedHashMap
from org.apache.commons.io import IOUtils
from org.json.simple import JSONArray
import os
import shutil
import sys

class TransitionWorkflow:
    def __init__(self):
        self.messaging = MessagingServices.getInstance()
            
    def run(self, context,  oid, fromWorkflowId, fromWorkflowStage, toWorkflowId, toWorkflowStage, pageTitle, label):
        self.log = context["log"]        
        self.storage = context["Services"].getStorage()
        self.object = self.storage.getObject(oid)
        self.workflowMetadata = self.object.getPayload("workflow.metadata")
        self.__tfpackage = None

        if(self.workflowMetadata is not None):
            self.updateWorkFlowMetadata(self.workflowMetadata, toWorkflowId, toWorkflowStage, pageTitle, label)
            self.updatePackageType(self._getTFPackage(), toWorkflowId)
            self.objectMetadata = self.object.getMetadata()            
            self.updateObjectMetadata(self.objectMetadata, toWorkflowId)
            self.object.close()
            self.sendMessage(oid)
        return True

    def sendMessage(self, oid):
        message = JsonObject()
        message.put("oid", oid)
        message.put("task", "reharvest")
        self.messaging.queueMessage(TransactionManagerQueueConsumer.LISTENER_ID, message.toString())
                
    def updateWorkFlowMetadata(self, workflowMetadata, toWorkflowId, toWorkflowStage, pageTitle, label):
        workflowMetaDataJson = JsonSimple(workflowMetadata.open()).getJsonObject()
        workflowMetaDataJson.put("id", toWorkflowId)
        workflowMetaDataJson.put("step", toWorkflowStage)
        workflowMetaDataJson.put("pageTitle", pageTitle)
        workflowMetaDataJson.put("label", label)
        inStream = IOUtils.toInputStream(workflowMetaDataJson.toString(), "UTF-8")
        try:
            StorageUtils.createOrUpdatePayload(self.object, "workflow.metadata", inStream)
        except StorageException:
            print " ERROR updating dataset payload"
    
    def updateObjectMetadata(self, objectMetaData, toWorkflowId):
        packageType, jsonConfigFile = self.__getPackageTypeAndJsonConfigFile(toWorkflowId)
        
        workflowsDir = FascinatorHome.getPathFile("harvest/workflows")
        configFile = File(workflowsDir, jsonConfigFile)
        configObject = StorageUtils.checkHarvestFile(self.storage, configFile);
        if configObject is None:
            oid = StorageUtils.generateOid(configFile);
            configObject = StorageUtils.getDigitalObject(self.storage, oid);
            
        objectMetaData.setProperty("jsonConfigPid", jsonConfigFile)
        objectMetaData.setProperty("jsonConfigOid", configObject.getId())
        
        configJson = JsonSimple(configFile)
        rulesFileName = configJson.getString(None, "indexer","script","rules")
        rulesFile = File(workflowsDir,rulesFileName)
        rulesObject = StorageUtils.checkHarvestFile(self.storage, rulesFile);
        if rulesObject is None:
            oid = StorageUtils.generateOid(rulesFile);
            rulesObject = StorageUtils.getDigitalObject(self.storage, oid);
        
        objectMetaData.setProperty("rulesPid", rulesFileName)
        objectMetaData.setProperty("rulesOid", rulesObject.getId())
        objectMetaData.setProperty("workflowTransitioned", "true")
        
        
    
    def updatePackageType(self, tfPackage, toWorkflowId):
        tfPackageJson = JsonSimple(tfPackage.open()).getJsonObject()
        tfPackageJson.put("packageType", toWorkflowId)
        
        inStream = IOUtils.toInputStream(tfPackageJson.toString(), "UTF-8")
        try:
            StorageUtils.createOrUpdatePayload(self.object, tfPackage.getId(), inStream)
        except StorageException:
            print " ERROR updating dataset payload"            

    def __getPackageTypeAndJsonConfigFile(self, packageType):
        try:
            types = JsonSimpleConfig().getJsonSimpleMap(["portal", "packageTypes"])
            pt = None
            if types is not None and not types.isEmpty():
                pt = types.get(packageType)
            if pt is None:
                configFile = "packaging-config.json"
            else:
                configFile = pt.getString("packaging-config.json", ["jsonconfig"])
        except Exception, e:
            configFile = "packaging-config.json"
        return (packageType, configFile)
        
        # Retrieve and parse the Fascinator Package from storage
    def _getTFPackage(self):
        if self.__tfpackage is None:
            payload = None
            inStream = None

            # We don't need to worry about close() calls here
            try:
                object = self.object
                sourceId = object.getSourceId()
                payload = None
                if sourceId is None or not sourceId.endswith(".tfpackage"):
                    # The package is not the source... look for it
                    for pid in object.getPayloadIdList():
                        if pid.endswith(".tfpackage"):
                            payload = object.getPayload(pid)
                            payload.setType(PayloadType.Source)
                else:
                    payload = object.getPayload(sourceId)

            except Exception, e:
                self.log.error("Error during package access", e)
                return None

        return payload




