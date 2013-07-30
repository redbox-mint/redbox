from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.api.storage import StorageException
from com.googlecode.fascinator.common import JsonObject, JsonSimple
from com.googlecode.fascinator.common.messaging import MessagingServices
from com.googlecode.fascinator.common.storage import StorageUtils
from com.googlecode.fascinator.common.solr import SolrResult
from com.googlecode.fascinator.messaging import TransactionManagerQueueConsumer
from org.apache.commons.fileupload.disk import DiskFileItemFactory
from org.apache.commons.fileupload.servlet import ServletFileUpload

from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.lang import Exception

class AttachmentsData:
    def __init__(self):
        self.messaging = MessagingServices.getInstance()

    def __activate__(self, context):
        self.velocityContext = context
        self.log = context["log"]
        self.formData = context["formData"]
       
        self.Services = context["Services"]
        self.oid = context["request"].getParameter("oid")
        self.attachmentType = context["request"].getParameter("attachmentType")
        result = None
        
        func = self.formData.get("func")
        self.log.debug("Func:%s" % func)
        if func == "attach-file":
            self.log.debug("---------attaching file-----------")
            result = self.__attachFile()
        elif func == "delete-attach-file":
            self.log.debug("---------deleting file-----------")
            result = self.__deleteAttachment()
        else:
            self.log.debug("---------listing files-----------")
            result = self.__listAttachments()
        writer = context["response"].getPrintWriter("text/plain; charset=UTF-8")
        writer.println(result)
        writer.close()
        
    def __listAttachments(self):
        attachedFiles = self.__getAttachedFiles(self.oid, self.attachmentType)
        return self.__toJson({
                "ok": "Completed OK",
                "oid": self.oid,
                "files": attachedFiles
            }) 

    def sendMessage(self, oid, eventType):
        message = JsonObject()
        message.put("oid", oid)
        message.put("eventType", eventType)
        message.put("username", self.vc("page").authentication.get_username())
        message.put("context", "Workflow")
        message.put("task", "workflow")
        self.messaging.queueMessage(
                TransactionManagerQueueConsumer.LISTENER_ID,
                message.toString())

    def __attachFile(self):
        try:
            # WebKit/IE prefixes C:\fakepath\ with javascript manipulated file inputs
            uploadFile = self.formData.get("uploadFile")
            self.log.debug(uploadFile)  
            self.log.debug(self.vc("sessionState").toString())
            self.log.debug(self.formData.toString())
            uploadFile = uploadFile.replace("C:\\fakepath\\", "")
            fileDetails = self.vc("sessionState").get(uploadFile)
            # Establish that we do have details on the uploaded file
            if fileDetails is None:
                #uploadFile = uploadFile.rsplit("\\", 1)[-1]
                fileDetails = self.vc("sessionState").get(uploadFile)
            if fileDetails is None:
                self.log.error("**** fileDetails is None!!! ***")
                return self.__toJson({
                    "error": "fileDetails is None (no upload file!)"
                })
            self.log.debug("Attach Upload: fileDetails: '{}'", fileDetails)

            errorDetails = fileDetails.get("error")
            if errorDetails:
                self.log.error("ERROR: %s" % errorDetails)
                return self.__toJson({"error": errorDetails})

            # Look for the storage info we need
            jsonFormData = JsonSimple(self.formData.get("json"))
            oid = jsonFormData.getString(None, "oid")
            fname = fileDetails.get("name")
            foid = fileDetails.get("oid")
            attachType = jsonFormData.getString("supporting-material", "attachmentType")
            self.log.debug("attach oid='{}', filename='{}', foid='{}'", [oid, fname, foid])

            # Make sure it was actually stored
            try:
                attachObj = self.Services.getStorage().getObject(foid)
            except StorageException, e:
                return JsonSimple({"error": "Attached file - '%s'" % str(e)})

            # Build up some metadata to store alongside the file
            attachFormData = JsonSimple(self.formData.get("json", "{}"))            
            attachMetadata = {
                "type": "attachment",
                "created_by": "attachments.py",
                "formData": {
                    "oid": foid,
                    "attached_to": oid,
                    "filename": fname,
                    "access_rights": attachFormData.getString("private", ["accessRights"]),
                    "attachment_type": attachType,
                    "description" : attachFormData.getString("", ["description"])
                }
            }

            # We are going to send an update on all attachments back with our response
            attachedFiles = self.__getAttachedFiles(oid, attachType)
            attachedFiles.append(dict(attachMetadata["formData"]))

            # Now store our metadata for this file
            try:
                jsonMetadata = self.__toJson(attachMetadata)
                jsonIn = ByteArrayInputStream(jsonMetadata.toString())
                StorageUtils.createOrUpdatePayload(attachObj, "attachments.metadata", jsonIn)
                jsonIn.close();
                attachObj.close();
            except StorageException, e:
                self.log.error("Failed to create attachment metadata!", e)

            # Re-Index the main object so it knows about all attachments
            indexer = self.Services.getIndexer()
            indexer.index(foid, "TF-OBJ-META")
            indexer.commit()

            # Notify our subscribers
            #self.sendMessage(oid, "Attachment '%s'" % fname)

            # Send a response back to the form
            #TODO - attachedFiles is missing OIDs here
            return self.__toJson({
                "ok": "Completed OK",
                "file" : attachMetadata["formData"],
                "files": attachedFiles
            })

        except Exception, e:
            return self.__toJson({"error":"__attachFile() - '%s'" % str(e)})

    def __deleteAttachment(self):
        try:
            oid = self.formData.get("oid")
            foid = self.formData.get("foid")
            if foid is None:
                return self.__toJson({"error": "__deleteAttachment() - FOID cannot be null"})
            self.log.debug("delete attachment oid='{}', foid='{}'", [oid, foid])
            attachedFiles = self.__getAttachedFiles(oid, self.attachmentType)

            # find
            delFileData = [i for i in attachedFiles if i["oid"] == foid]
            if delFileData is not None:
                self.log.debug("delFileData = '{}'", str(delFileData))
                attachedFiles.remove(delFileData[0])

                errors = False
                # Delete from storage
                try:
                    self.Services.storage.removeObject(foid)
                except Exception, e:
                    self.log.error("Error deleting object from storage: ", e)
                    errors = True

                # Delete from Solr
                try:
                    indexer = self.Services.getIndexer()
                    indexer.remove(foid)
                except Exception, e:
                    self.vc["log"].error("Error deleting Solr entry: ", e)
                    errors = True

                # Delete annotations
                try:
                    indexer.annotateRemove(foid)
                except Exception, e:
                    self.log.error("Error deleting annotations: ", e)
                    errors = True

                # Solr commit
                try:
                    indexer.commit()
                except Exception, e:
                    self.log.error("Error during Solr commit: ", e)
                    errors = True

                # Notify our subscribers
                #self.sendMessage(oid, "Delete Attachment %s" % str(delFileData))

                if errors:
                    return self.__toJson({"error":"Failed to delete attachment, please check system logs"})

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

    def __getAttachedFiles(self, oid, attachType):
        response = self.__search("attached_to:%s AND attachment_type:%s" % (oid, attachType))
        files = [{
            "oid": doc.get("storage_id"),
            "filename": doc.getFirst("filename"),
            "attachment_type": doc.getFirst("attachment_type"),
            "access_rights": doc.getFirst("access_rights"),
            "description" : doc.getFirst("description")
        } for doc in response.getResults()]
        files.sort(lambda a,b: cmp(a["filename"], b["filename"]))
        return files

    def __updateWorkflow(self):
        result = { "error":"An unknown error has occurred" }
        # execute the workflow step templates, disregarding the resulting html
        if self.prepareTemplate():
            # renderTemplate requires all formData, not just local
            tempFormData = self.localFormData
            self.localFormData = self.formData
            self.renderTemplate()
            self.localFormData = tempFormData
            # Notify our subscribers
            oid = self.getOid()
            #self.sendMessage(oid, "Save")
            result = { "ok":"Workflow updated", "oid":oid }
        else:
            self.log.debug(self.errorMsg)
            result = { "error": self.errorMsg }
        return self.__toJson(result)

    def __toJson(self, dataDict):
        return JsonSimple(JsonObject(dataDict))

    # Get from velocity context
    def vc(self, index):
        if self.velocityContext[index] is not None:
            return self.velocityContext[index]
        else:
            log.error("ERROR: Requested context entry '" + index + "' doesn't exist")
            return None