from au.edu.usq.fascinator.common import JsonSimple
from au.edu.usq.fascinator.api.storage import StorageException
from java.io import ByteArrayInputStream
from org.apache.commons.lang import StringEscapeUtils

class WorkflowStage:
    def __init__(self, json):
        self.__json = json

    def getName(self):
        return self.__json.getString("noname", ["name"])

    def getLabel(self):
        return self.__json.getString("[No label]", ["label"])

    def getDescription(self):
        return self.__json.getString("No description.", ["description"])

class SubmissionData(object):
    def __activate__(self, context):
        self.__services = context["Services"]
        self.__formData = context["formData"]
        self.__oid = self.__formData.get("oid")
        self.__object = None
        self.__errorMessage = None
        self.__workflow = None
        self.__workflow = self.__getWorkflow()
        func = self.__formData.get("func")
        ajax = self.__formData.get("ajax")
        if ajax and func == "update-package-meta-deposit":
            result = self.__update()
            writer = response.getPrintWriter("application/json; charset=UTF-8")
            writer.println(result)
            writer.close()
        else:
            self.__requestData = self.__getRequestData()
        if self.__errorMessage:
            print "Error: %s" % self.__errorMessage

    def getFormData(self, field):
        return StringEscapeUtils.escapeHtml(self.__formData.get(field, ""))

    def getRequestData(self, field):
        return StringEscapeUtils.escapeHtml(self.__requestData.getString("", [field]))

    def getOid(self):
        return self.__oid

    def getCurrentStep(self):
        return self.__workflow.getString(None, ["step"])

    def getErrorMessage(self):
        return self.__errorMessage

    def __getRequestData(self):
        data = None
        object = self.__getObject()
        payload = object.getPayload(object.getSourceId())
        data = JsonSimple(payload.open())
        payload.close()
        return data

    def __getWorkflow(self):
        if self.__getObject() and self.__workflow is None:
            try:
                wfPayload = self.__object.getPayload("workflow.metadata")
                self.__workflow = JsonSimple(wfPayload.open())
                wfPayload.close()
            except StorageException, e:
                self.__errorMessage = "Failed to retrieve workflow metadata: " + e.getMessage()
        return self.__workflow

    def __getObject(self):
        if not self.__object:
            try:
                self.__object = self.__services.storage.getObject(self.__oid)
            except StorageException, e:
                self.__errorMessage = "Failed to retrieve object: " + e.getMessage()
                return None
        return self.__object

    def __update(self):
        print "Updating '%s'" % self.__oid
        result = '{"ok":"Updated OK"}'

        json = self.__workflow.getJsonObject()
        json.put("step", "live")
        json.put("label", "Processed")
        json.put("accepted", True)

        self.__getObject().updatePayload("workflow.metadata",
                ByteArrayInputStream(json.toString()))

        self.__services.indexer.index(self.__oid)
        self.__services.indexer.commit()
        return result

