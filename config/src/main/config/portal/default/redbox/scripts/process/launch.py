from java.lang import String

from com.googlecode.fascinator.common import JsonSimple
from com.googlecode.fascinator.common import FascinatorHome
from java.util import HashMap
from java.io import File
from java.lang import Class
import sys
#
class LaunchData:

    def __init__(self):
        pass
    def __activate__(self, context):
        self.log = context["log"]
        self.request = context["request"]
        self.sessionState = context["sessionState"]
        self.sessionState.set("username","admin")
        processingSet = self.request.getParameter("processingSet")
        self.procMsg = None
        # read configuration and trigger processing stream sets
        # storing the return object on the map
        configFilePath = FascinatorHome.getPath("process")+"/processConfig.json"
        procConfigFile = File(configFilePath)
        if procConfigFile.exists() == True:
            self.dataMap = HashMap()
            self.dataMap.put("indexer", context['Services'].getIndexer())
            self.procConfigJson = JsonSimple(procConfigFile)
            for configObj in self.procConfigJson.getJsonArray():
                configJson = JsonSimple(configObj)
                procId = configJson.getString("", "id")
                if processingSet is not None: 
                    if procId == processingSet:
                        self.execProcSet(procId, configJson)
                else:
                    self.execProcSet(procId, configJson)
            if self.procMsg is None:
                self.procMsg = "Processing complete!"
        else:
            self.procMsg = "Configuration file does not exist: " + configFilePath
            
    def execProcSet(self, procId, configJson):
        self.execProcessors(procId, configJson, self.dataMap, "pre")
        self.execProcessors(procId, configJson, self.dataMap, "main")
        self.execProcessors(procId, configJson, self.dataMap, "post")
        
    def execProcessors(self, procId, configJson, dataMap, stageName):
        for procObj in configJson.getArray(stageName):
            procJson = JsonSimple(procObj)
            procClassName = procJson.getString("", "class")
            procConfigPath = procJson.getString("", "config")
            
            procInputKey = procJson.getString("", "inputKey")
            procOutputKey = procJson.getString("", "outputKey")
            procClass = Class.forName(procClassName)
            procInst = procClass.newInstance()
            
            procMethod = procClass.getMethod("process", self.get_class("java.lang.String"),self.get_class("java.lang.String"), self.get_class("java.lang.String"),self.get_class("java.lang.String"),self.get_class("java.lang.String"), self.get_class("java.util.HashMap"))
            procMethod.invoke(procInst, procId, procInputKey, procOutputKey, stageName, procConfigPath, dataMap)
            
        
    # Standard Java Class forName seems to have issues at least with Interfaces. 
    # This is an alternative method taken from http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname    
    def get_class(self, kls):
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__( module )
        for comp in parts[1:]:
            m = getattr(m, comp)            
        return m    
    
    def getProcMsg(self):
        return self.procMsg
        
    