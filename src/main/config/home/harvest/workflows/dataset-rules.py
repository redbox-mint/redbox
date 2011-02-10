from au.edu.usq.fascinator.api.storage import StorageException
from au.edu.usq.fascinator.common import FascinatorHome, JsonConfigHelper
from au.edu.usq.fascinator.common.storage import StorageUtils
from java.io import ByteArrayInputStream, StringWriter
from java.lang import String
from org.apache.commons.io import IOUtils

import sys
import time
pathToWorkflows = FascinatorHome.getPath("harvest/workflows")
if sys.path.count(pathToWorkflows) == 0:
    sys.path.append(pathToWorkflows)
from json2 import read as jsonReader

class IndexData:
    def __activate__(self, context):
        print " * Running dataset-rules.py..."

        # Prepare variables
        self.index = context["fields"]
        self.object = context["object"]
        self.payload = context["payload"]
        self.params = context["params"]
        self.utils = context["pyUtils"]
        self.config = context["jsonConfig"]

        # Common data
        self.__newDoc()

        # Real metadata
        if self.itemType == "object":
            self.__basicData()
            self.__metadata()
            # Some of the above steps may request some
            #  messages be sent, particularly workflows
            self.__messages()

        # Make sure security comes after workflows
        self.__security()

    def __newDoc(self):
        self.oid = self.object.getId()
        self.pid = self.payload.getId()
        metadataPid = self.params.getProperty("metaPid", "DC")

        if self.pid == metadataPid:
            self.itemType = "object"
        else:
            self.oid += "/" + self.pid
            self.itemType = "datastream"
            self.utils.add(self.index, "identifier", self.pid)

        self.utils.add(self.index, "id", self.oid)
        self.utils.add(self.index, "storage_id", self.oid)
        self.utils.add(self.index, "item_type", self.itemType)
        self.utils.add(self.index, "last_modified", time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        self.utils.add(self.index, "harvest_config", self.params.getProperty("jsonConfigOid"))
        self.utils.add(self.index, "harvest_rules",  self.params.getProperty("rulesOid"))
        self.utils.add(self.index, "display_type", "package-dataset")

        self.item_security = []
        self.owner = self.params.getProperty("owner", None)

    def __basicData(self):
        self.utils.add(self.index, "repository_name", self.params["repository.name"])
        self.utils.add(self.index, "repository_type", self.params["repository.type"])

    def __security(self):
        # Security
        roles = self.utils.getRolesWithAccess(self.oid)
        if roles is not None:
            # For every role currently with access
            for role in roles:
                # Should show up, but during debugging we got a few
                if role != "":
                    if role in self.item_security:
                        # They still have access
                        self.utils.add(self.index, "security_filter", role)
                    else:
                        # Their access has been revoked
                        self.__revokeAccess(role)
            # Now for every role that the new step allows access
            for role in self.item_security:
                if role not in roles:
                    # Grant access if new
                    self.__grantAccess(role)
                    self.utils.add(self.index, "security_filter", role)

        # No existing security
        else:
            if self.item_security is None:
                # Guest access if none provided so far
                self.__grantAccess("guest")
                self.utils.add(self.index, "security_filter", role)
            else:
                # Otherwise use workflow security
                for role in self.item_security:
                    # Grant access if new
                    self.__grantAccess(role)
                    self.utils.add(self.index, "security_filter", role)
        # Ownership
        if self.owner is None:
            self.utils.add(self.index, "owner", "system")
        else:
            self.utils.add(self.index, "owner", self.owner)

    def __indexList(self, name, values):
        for value in values:
            self.utils.add(self.index, name, value)

    def __grantAccess(self, newRole):
        schema = self.utils.getAccessSchema("derby");
        schema.setRecordId(self.oid)
        schema.set("role", newRole)
        self.utils.setAccessSchema(schema, "derby")

    def __revokeAccess(self, oldRole):
        schema = self.utils.getAccessSchema("derby");
        schema.setRecordId(self.oid)
        schema.set("role", oldRole)
        self.utils.removeAccessSchema(schema, "derby")

    def __metadata(self):
        self.titleList = ["New Dataset"]
        self.descriptionList = []
        self.creatorList = []
        self.creationDate = []
        self.contributorList = []
        self.approverList = []
        self.formatList = ["application/x-fascinator-package"]
        self.fulltext = []
        self.relationDict = {}
        self.customFields = {}

        # Try our data sources, order matters
        self.__workflow()

        # Some defaults if the above failed
        if self.titleList == []:
           self.titleList.append(self.object.getSourceId())
        if self.formatList == []:
            source = self.object.getPayload(self.object.getSourceId())
            self.formatList.append(source.getContentType())

        # Index our metadata finally
        self.__indexList("dc_title", self.titleList)
        self.__indexList("dc_creator", self.creatorList)  #no dc_author in schema.xml, need to check
        self.__indexList("dc_contributor", self.contributorList)
        self.__indexList("dc_description", self.descriptionList)
        self.__indexList("dc_format", self.formatList)
        self.__indexList("dc_date", self.creationDate)
        self.__indexList("full_text", self.fulltext)
        for key in self.customFields:
            self.__indexList(key, self.customFields[key])
        for key in self.relationDict:
            self.__indexList(key, self.relationDict[key])

    def __workflow(self):
        # Workflow data
        WORKFLOW_ID = "dataset"
        wfChanged = False
        workflow_security = []
        self.message_list = None
        try:
            wfPayload = self.object.getPayload("workflow.metadata")
            wfMeta = JsonConfigHelper(wfPayload.open())
            wfPayload.close()
            wfMeta.set("pageTitle", "Dataset Metadata")
            # Are we indexing because of a workflow progression?
            targetStep = wfMeta.get("targetStep")
            if targetStep is not None and targetStep != wfMeta.get("step"):
                wfChanged = True
                # Step change
                wfMeta.set("step", targetStep)
                wfMeta.removePath("targetStep")
            # This must be a re-index then
            else:
                targetStep = wfMeta.get("step")
            # Security change
            stages = self.config.getJsonList("stages")
            for stage in stages:
                if stage.get("name") == targetStep:
                    wfMeta.set("label", stage.get("label"))
                    self.item_security = stage.getList("visibility")
                    workflow_security = stage.getList("security")
                    if wfChanged == True:
                        self.message_list = stage.getList("message")

        except StorageException:
            # No workflow payload, time to create
            wfChanged = True
            wfMeta = JsonConfigHelper()
            wfMeta.set("id", WORKFLOW_ID)
            wfMeta.set("step", "investigation")
            wfMeta.set("pageTitle", "Dataset Metadata")
            stages = self.config.getJsonList("stages")
            for stage in stages:
                if stage.get("name") == "investigation":
                    wfMeta.set("label", stage.get("label"))
                    self.item_security = stage.getList("visibility")
                    workflow_security = stage.getList("security")
                    self.message_list = stage.getList("message")

        # Has the workflow metadata changed?
        if wfChanged == True:
            jsonString = String(wfMeta.toString())
            inStream = ByteArrayInputStream(jsonString.getBytes("UTF-8"))
            try:
                StorageUtils.createOrUpdatePayload(self.object, "workflow.metadata", inStream)
            except StorageException:
                print " * ERROR updating dataset payload!"

        # Form processing
        formData = wfMeta.getJsonList("formData")
        if formData.size() > 0:
            formData = formData[0]
        else:
            formData = None
        coreFields = ["title", "description", "manifest", "metaList"]
        if formData is not None:
            # Core fields
            title = formData.getList("title")
            if title:
                self.titleList = title
            description = formData.getList("description")
            if description:
                self.descriptionList = description
            # Non-core fields
            data = formData.getMap("/")
            for field in data.keySet():
                if field not in coreFields:
                    self.customFields[field] = formData.getList(field)

        # Manifest processing (formData is not present in wfMeta)
        manifest = self.__getManifest()
        self.titleList = [manifest.get("title", "Untitled")]
        self.descriptionList = [manifest.get("description", "")]
        for field in manifest.iterkeys():
            if field not in coreFields:
                value = manifest.get(field)
                if value is not None and value.strip() != "":
                    self.utils.add(self.index, field, value)
                    if field.startswith("dc:") and \
                            not (field.endswith(".dc:identifier") \
                              or field.endswith(".rdf:resource") \
                              or field.endswith(".association")):
                        # index dublin core fields for faceting
                        facetField = field.replace("dc:", "dc_")
                        dot = field.find(".")
                        if dot > 0:
                            facetField = facetField[:dot]
                        #print "Indexing DC field '%s':'%s'" % (field, facetField)
                        self.utils.add(self.index, facetField, value)

        # Workflow processing
        self.utils.add(self.index, "workflow_id", wfMeta.get("id"))
        self.utils.add(self.index, "workflow_step", wfMeta.get("step"))
        self.utils.add(self.index, "workflow_step_label", wfMeta.get("label"))
        for group in workflow_security:
            self.utils.add(self.index, "workflow_security", group)
            if self.owner is not None:
                self.utils.add(self.index, "workflow_security", self.owner)

    def __messages(self):
        if self.message_list is not None and len(self.message_list) > 0:
            msg = JsonConfigHelper()
            msg.set("oid", self.oid)
            message = msg.toString()
            for target in self.message_list:
                self.utils.sendMessage(target, message)

    def __getManifest(self):
        return self.__getJsonPayload(self.object.getSourceId())

    def __getJsonPayload(self, pid):
        payload = self.object.getPayload(pid)
        writer = StringWriter()
        IOUtils.copy(payload.open(), writer)
        dataDict = jsonReader(writer.toString())
        payload.close()
        return dataDict

