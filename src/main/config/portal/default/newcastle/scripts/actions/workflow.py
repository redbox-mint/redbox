from workflow import WorkflowData as DefaultWorkflowData

from au.edu.usq.fascinator.api.indexer import SearchRequest
from au.edu.usq.fascinator.api.storage import StorageException
from au.edu.usq.fascinator.common import JsonObject, JsonSimple, MessagingServices
from au.edu.usq.fascinator.common.storage import StorageUtils
from au.edu.usq.fascinator.common.solr import SolrResult

from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.lang import Exception

class WorkflowData(DefaultWorkflowData):
    def __init__(self):
        DefaultWorkflowData.__init__(self)
        self.messaging = MessagingServices.getInstance()

    def __activate__(self, context):
        self.log = context["log"]
        self.formData = context["formData"]
        self.Services = context["Services"]
        #self.log.debug("formData='%s'" % self.formData)

        result = None
        isAjax = bool(self.formData.get("ajax")) or context["request"].isXHR()
        if isAjax:
            self.setup(context)
            # handle ajax requests according to the func param, methods are
            # expected to return a JsonSimple object
            func = self.formData.get("func")
            if func == "attach-file":
                result = self.__attachFile()
            elif func == "delete-attach-file":
                result = self.__deleteAttachment()
            else:
                self.formProcess = func is None
                if self.formProcess:
                    self.processForm()
                    result = '{"ok":"Processed Form Data"}'
                else:
                    result = self.__updateWorkflow()
            writer = context["response"].getPrintWriter("application/json; charset=UTF-8")
            writer.println(result)
            writer.close()
        else:
            # standard workflow processing
            DefaultWorkflowData.__activate__(self, context)

    def processForm(self):
        DefaultWorkflowData.processForm(self)
        # Notify our subscribers
        self.sendMessage(self.getOid(), "Update")

    def sendMessage(self, oid, eventType):
        self.messaging.onEvent({
            "oid": oid,
            "eventType": eventType,
            "username": self.vc("page").authentication.get_username(),
            "context": "Workflow"
        })

    def __attachFile(self):
        try:
            # WebKit/IE prefixes C:\fakepath\ with javascript manipulated file inputs
            uploadFile = self.formData.get("uploadFile")
            uploadFile = uploadFile.replace("C:\\fakepath\\", "")
            fileDetails = self.vc("sessionState").get(uploadFile)

            #self.log.debug("fileDetails:%s" % fileDetails)
            errorDetails = fileDetails.get("error")
            if errorDetails:
                self.log.error("ERROR: %s" % errorDetails)
                return self.__toJson({"error": errorDetails})

            jsonFormData = JsonSimple(self.formData.get("json"))
            oid = jsonFormData.getString(None, "oid")
            fname = fileDetails.get("name")
            foid = fileDetails.get("oid")
            #self.log.debug("attach oid='%s', filename='%s', foid='%s'" % (oid, fname, foid))
            try:
                attachObj = self.Services.getStorage().getObject(foid)
            except StorageException, e:
                return JsonSimple({"error":"Attached file - '%s'" % str(e)})

            attachFormData = JsonSimple(self.formData.get("json", "{}"))
            attachMetadata = {
                "type": "attachment",
                "created_by": "workflow.py",
                "formData": {
                    "oid": foid,
                    "attached_to": oid,
                    "filename": fname,
                    "access_rights": attachFormData.getString("private", ["accessRights"]),
                    "attachment_type": attachFormData.getString("supporting-material", ["attachmentType"])
                }
            }
            attachedFiles = self.__getAttachedFiles(oid)
            attachedFiles.append(dict(attachMetadata["formData"]))
            try:
                jsonMetadata = self.__toJson(attachMetadata)
                jsonIn = ByteArrayInputStream(jsonMetadata.toString())
                StorageUtils.createOrUpdatePayload(attachObj, "workflow.metadata", jsonIn)
            except StorageException, e:
                self.log.error("Failed to create attachment metadata! %s" % str(e))

            indexer = self.Services.getIndexer()
            indexer.index(foid, "TF-OBJ-META")      # reindex main object only
            indexer.commit()

            # Notify our subscribers
            self.sendMessage(foid, "Attachment")

            return self.__toJson({
                "ok": "Completed OK",
                "oid": foid,
                "attachedFiles": attachedFiles
            })
        except Exception, e:
            return self.__toJson({"error":"__attachFile() - '%s'" % str(e)})

    def __deleteAttachment(self):
        try:
            oid = self.formData.get("oid")
            foid = self.formData.get("foid")
            self.log.debug("delete attachment oid='%s', foid='%s'" % (oid, foid))
            attachedFiles = self.__getAttachedFiles(oid)
            # find
            delFileData = [i for i in attachedFiles if i["id"]==foid]
            if delFileData:
                #print "delFileData='%s'" % str(delFileData)
                attachedFiles.remove(delFileData[0])
                try:
                    indexer = self.Services.getIndexer()
                    indexer.remove(foid)
                    indexer.commit()
                    # Notify our subscribers
                    self.sendMessage(oid, "Delete")
                    self.Services.storage.removeObject(foid)
                except Exception, e:
                    self.log.error("Failed to delete attachment '%s'" % str(e))
            return self.__toJson({"ok":"Deleted OK", "attachedFiles":attachedFiles})
        except Exception, e:
            self.log.error("ERROR: %s" % str(e))
            return self.__toJson({"error":"__deleteAttachment() - '%s'" % str(e)})

    def __search(self, query):
        req = SearchRequest(query)
        req.setParam("rows", "1000")
        out = ByteArrayOutputStream()
        self.Services.indexer.search(req, out)
        return SolrResult(ByteArrayInputStream(out.toByteArray()))

    def __getAttachedFiles(self, oid):
        response = self.__search("attached_to:%s" % oid)
        files = [{
            "id": doc.get("id"),
            "filename": doc.getFirst("filename"),
            "attachment_type": doc.getFirst("attachment_type"),
            "access_rights": doc.getFirst("access_rights")
        } for doc in response.getResults()]
        files.sort(lambda a,b: cmp(a["filename"], b["filename"]))
        return files

    def __updateWorkflow(self):
        # execute the workflow step templates, disregarding the resulting html
        if self.prepareTemplate():
            # renderTemplate requires all formData, not just local
            tempFormData = self.localFormData
            self.localFormData = self.formData
            self.renderTemplate()
            self.localFormData = tempFormData
        # Notify our subscribers
        oid = self.getOid()
        self.sendMessage(oid, "Save")
        return self.__toJson({ "ok":"Submitted OK", "oid": oid })

    def __toJson(self, dataDict):
        return JsonSimple(JsonObject(dataDict))
