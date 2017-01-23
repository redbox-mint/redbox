from com.googlecode.fascinator.common import JsonSimple, JsonObject
from com.googlecode.fascinator.common import FascinatorHome
from com.googlecode.fascinator.spring import ApplicationContextProvider
from com.googlecode.fascinator.common.messaging import MessagingServices
from com.googlecode.fascinator import ReIndexClient
from org.json.simple import JSONArray
from org.apache.commons.io import FileUtils
from java.io import File
from java.util import UUID


class SystemSettingsData:

    def __init__(self):
        pass

    def __activate__(self, context):
        self.velocityContext = context
        self.log = self.velocityContext["log"]
        self.formData = self.velocityContext["formData"]
        self.request = self.velocityContext["request"]
        self.sysConfig = self.velocityContext["systemConfig"]
        self.maintenanceModeService = ApplicationContextProvider.getApplicationContext().getBean("maintenanceModeService")
        if self.request.getMethod() == "POST":
            if self.formData.get("action") == "Save":
                self.saveChanges()
            if self.formData.get("action") == "RunReindex":
                self.reindex()

    def maintenanceModeEnabled(self):
        return self.maintenanceModeService.isMaintanceMode()

    def reindex(self):
        scriptString = self.sysConfig.getString(None, "restoreTool",
                "migrationScript");

        harvestRemap = self.sysConfig.getBoolean(False, "restoreTool",
                "harvestRemap", "enabled");
        oldHarvestFiles = self.sysConfig.getBoolean(False, "restoreTool",
                "harvestRemap", "allowOlder");
        failOnMissing = self.sysConfig.getBoolean(True, "restoreTool",
                "harvestRemap", "failOnMissing");
        messaging = MessagingServices.getInstance()
        message = JsonObject()
        message.put("migrationScript", scriptString)
        harvestRemapObject = JsonObject()
        harvestRemapObject.put("enabled", harvestRemap)
        harvestRemapObject.put("allowOlder", oldHarvestFiles)
        harvestRemapObject.put("failOnMissing", failOnMissing)

        message.put("harvestRemap", harvestRemapObject)
        messaging.queueMessage("reindex", message.toJSONString())

    def saveChanges(self):
        if self.formData.get("maintenanceMode") == "Enabled":
            self.maintenanceModeService.toggleMaintenanceMode(True)
        else:
            self.maintenanceModeService.toggleMaintenanceMode(False)
