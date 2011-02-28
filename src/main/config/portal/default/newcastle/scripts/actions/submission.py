import uuid
from au.edu.usq.fascinator import HarvestClient
from au.edu.usq.fascinator.common import FascinatorHome, JsonObject
from java.io import File
from org.apache.commons.io import FileUtils

class SubmissionData:
    def __activate__(self, context):
        self.sessionState = context["sessionState"]
        self.formData = context["formData"]
        self.response = context["response"]
        print "formData:", formData
        submissionFile = self.__createSubmission(formData)
        self.__harvest(submissionFile)
        result = '{"ok":"Submitted OK"}'
        writer = response.getPrintWriter("application/json; charset=UTF-8")
        writer.println(result)
        writer.close()

    def __createSubmission(self, formData):
        jsonData = JsonObject()
        jsonData.put("description", formData.get("description"))
        jsonData.put("contactName", formData.get("contactName"))
        jsonData.put("emailAddress", formData.get("emailAddress"))
        jsonData.put("phoneNumber", formData.get("phoneNumber"))
        filename = "%s.json" % uuid.uuid4()
        jsonFile = File(FascinatorHome.getPathFile("submissions"), filename)
        print "jsonFile:", jsonFile
        print "jsonData:", jsonData.toString()
        FileUtils.writeStringToFile(jsonFile, jsonData.toString(), "UTF-8")
        return jsonFile

    def __harvest(self, submissionFile):
        username = self.sessionState.get("username")
        if username is None:
            username = "guest" # necessary?
        harvester = None
        workflowsDir = FascinatorHome.getPathFile("harvest/workflows")
        configFile = File(workflowsDir, "submission.json")
        harvester = HarvestClient(configFile, submissionFile, username)
        harvester.start()
        oid = harvester.getUploadOid()
        harvester.shutdown()
        return oid
