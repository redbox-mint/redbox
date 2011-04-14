import time
from au.edu.usq.fascinator.common import JsonSimple
from au.edu.usq.fascinator.api.storage import StorageException
from java.io import ByteArrayInputStream
from org.apache.commons.lang import StringEscapeUtils

def truncate(s, maxLength):
    return s[:maxLength] + (s[maxLength:] and "...")

class SubmissionData:
    def __activate__(self, context):
        self.__services = context["Services"]
        self.__formData = context["formData"]
        self.__auth = context["page"].authentication
        self.__oid = self.__formData.get("oid")
        self.__object = self.__getObject();
        self.__errorMessage = None
        self.__requestData = self.__getJsonData(self.__object.getSourceId())
        self.__workflowData = self.__getJsonData("workflow.metadata")
        
        #print " ***** formData:", self.__formData
        #print " ***** requestData:", self.__requestData
        #print " ***** workflowData:", self.__workflowData

        if self.__formData.get("func") == "update-package-meta-deposit":
            result = self.__update()
            writer = context["response"].getPrintWriter("application/json; charset=UTF-8")
            writer.println(result)
            writer.close()
        if self.__errorMessage:
            print "Error: %s" % self.__errorMessage

    def getFormData(self, field):
        return StringEscapeUtils.escapeHtml(self.__formData.get(field, ""))

    def getRequestData(self, field):
        return StringEscapeUtils.escapeHtml(self.__requestData.getString("", [field]))

    def getOid(self):
        return self.__oid

    def getCurrentStep(self):
        return self.__workflowData.getString(None, ["step"])

    def isSubmitted(self):
        return self.__requestData.getBoolean(False, ["submitted"])

    def getSubmitDate(self):
        return self.__requestData.getString(time.strftime("%Y-%m-%d %I:%M:%S %p"), ["submitDate"])

    def getErrorMessage(self):
        return self.__errorMessage

    def __getJsonData(self, pid):
        data = None
        object = self.__getObject()
        payload = object.getPayload(pid)
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
        obj = None
        try:
            obj = self.__services.storage.getObject(self.__oid)
        except StorageException, e:
            self.__errorMessage = "Failed to retrieve object: " + e.getMessage()
            return None
        return obj

    def __update(self):
        print "Updating '%s'" % self.__oid
        result = '{"ok":"Updated OK"}'

        if self.__formData.get("acceptOnly", "false") == "false":
            # update from form data
            data = self.__requestData.getJsonObject()
            formFields = self.__formData.getFormFields()
            for formField in formFields:
                data.put(formField, self.__formData.get(formField))
            description = self.__formData.get("submitDescription", "[No description]")
            data.put("title", truncate(description, 25))
            self.__updatePayload(self.__object.getSourceId(), data)

        # update workflow metadata
        if self.__auth.is_logged_in():
            wf = self.__workflowData.getJsonObject()
            wf.put("step", "investigation")
            wf.put("label", "Investigation")
            wf.put("pageTitle", "Metadata Record")
            self.__updatePayload("workflow.metadata", wf)
            # update ownership to the one who accepted the submission
            self.__object.getMetadata().setProperty("owner", self.__auth.get_username())
        else:
            # update ownership so guest users cannot see submission requests
            self.__object.getMetadata().setProperty("owner", "system")
        self.__object.close();

        self.__services.indexer.index(self.__oid)
        self.__services.indexer.commit()
        return result

    def __updatePayload(self, pid, data):
        self.__object.updatePayload(pid, ByteArrayInputStream(data.toString()))
