import time

from com.googlecode.fascinator.api.storage import StorageException
from com.googlecode.fascinator.common import JsonSimple
from com.googlecode.fascinator.common.storage import StorageUtils
from java.util import HashSet
from org.apache.commons.io import IOUtils
import imp

class BaseIndexData(object):

    def __activate__(self, context):
       
        # Prepare variables
        self.index = context["fields"]
        self.object = context["object"]
        self.payload = context["payload"]
        self.params = context["params"]
        self.utils = context["pyUtils"]
        self.config = context["jsonConfig"]
        self.log = context["log"]
        
        self.log.debug("Indexing Metadata Record '{}' '{}'", self.object.getId(), self.payload.getId())
        
        # Common data
        self.user_id = "" # Used for setting ownership when data is harvested by (New)Alert with user_id instead of user is available
        self.__newDoc()
        self.packagePid = None
        pidList = self.object.getPayloadIdList()
        for pid in pidList:
            if pid.endswith(".tfpackage"):
                self.packagePid = pid

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

        self.utils.add(self.index, "storage_id", self.oid)
        if self.pid == metadataPid:
            self.itemType = "object"
        else:
            self.oid += "/" + self.pid
            self.itemType = "datastream"
            self.utils.add(self.index, "identifier", self.pid)

        self.utils.add(self.index, "id", self.oid)
        self.utils.add(self.index, "item_type", self.itemType)
        self.utils.add(self.index, "last_modified", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        self.utils.add(self.index, "harvest_config", self.params.getProperty("jsonConfigOid"))
        self.utils.add(self.index, "harvest_rules",  self.params.getProperty("rulesOid"))

        self.item_security = []
        self.owner = self.params.getProperty("owner", self.config.getString("guest", ["default-owner"]))

    def __basicData(self):
        self.utils.add(self.index, "repository_name", self.params["repository.name"])
        self.utils.add(self.index, "repository_type", self.params["repository.type"])
        # VITAL integration
        vitalPid = self.params["vitalPid"]
        if vitalPid is not None:
            self.utils.add(self.index, "vitalPid", vitalPid)
        # Persistent Identifiers
        pidProperty = self.config.getString(None, ["curation", "pidProperty"])
        if pidProperty is None:
            self.log.error("No configuration found for persistent IDs!")
        else:
            pid = self.params[pidProperty]
            if pid is not None:
                self.utils.add(self.index, "known_ids", pid)
                self.utils.add(self.index, "pidProperty", pid)
                self.utils.add(self.index, "oai_identifier", pid)
        self.utils.add(self.index, "oai_set", "default")
        # Publication
        published = self.params["published"]
        if published is not None:
            self.utils.add(self.index, "published", "true")

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
                        self.__revokeRoleAccess(role)
            # Now for every role that the new step allows access
            for role in self.item_security:
                if role not in roles:
                    # Grant access if new
                    self.__grantRoleAccess(role)
                    self.utils.add(self.index, "security_filter", role)

        # No existing security
        else:
            if self.item_security is None:
                # set the default owner to have access if none provided so far
                self.__grantRoleAccess(self.config.getString("guest", ["default-owner"]))
                self.utils.add(self.index, "security_filter", role)
            else:
                # Otherwise use workflow security
                for role in self.item_security:
                    # Grant access if new
                    self.__grantRoleAccess(role)
                    self.utils.add(self.index, "security_filter", role)
        
        users = self.utils.getUsersWithAccess(self.oid)
        if users is not None:
            # For every role currently with access
            for user in users:
                self.utils.add(self.index, "security_exception", user)

        # Ownership
        if self.owner is None:
            self.utils.add(self.index, "owner", "system")
        else:
            if self.owner == 'guest' and self.user_id != "":
                self.log.debug("baseRule.py: Need to assign ownership by mapping user_id to user because user_id and default owner 'guest' are found.")
                newOwner = self.__getUser()
                if newOwner is not None:
                    self.log.debug("baseRule.py: now reassign it to {}.", newOwner)
                    self.params["owner"] = newOwner
                    self.owner = newOwner
            self.utils.add(self.index, "owner", self.owner) 
#         owner = 'system'
#         if self.owner:
#             if self.owner == 'guest' and self.user_id != "":
#                 self.log.debug("baseRule.py: Need to assign ownership by mapping user_id to user because user_id and default owner 'guest' are found.")
#                 newOwner = self.__getUser(self.user_id)
#                 if newOwner is not None:
#                     self.params['owner'] = newOwner
#                     owner = newOwner
#             else:
#                 owner = self.owner
#         self.utils.add(self.index, "owner", owner)

    def __indexList(self, name, values):
        # convert to set so no duplicate values
        for value in HashSet(values):
            self.utils.add(self.index, name, value)

    def __grantRoleAccess(self, newRole):
        schema = self.utils.getAccessSchema();
        schema.setRecordId(self.oid)
        schema.set("role", newRole)
        self.utils.setAccessSchema(schema)
        
    def __grantUserAccess(self, newUser):
        schema = self.utils.getAccessSchema();
        schema.setRecordId(self.oid)
        schema.set("user", newUser)
        self.utils.setAccessSchema(schema)

    def __revokeRoleAccess(self, oldRole):
        schema = self.utils.getAccessSchema();
        schema.setRecordId(self.oid)
        schema.set("role", oldRole)
        self.utils.removeAccessSchema(schema)
        
    def __revokeUserAccess(self, oldUser):
        schema = self.utils.getAccessSchema();
        schema.setRecordId(self.oid)
        schema.set("user", oldUser)
        self.utils.removeAccessSchema(schema)

        
    def __metadata(self):
        self.title = None
        self.dcType = None
        self.descriptionList = []
        self.creatorList = []
        self.creationDate = []
        self.contributorList = []
        self.approverList = []
        self.formatList = ["application/x-fascinator-package"]
        self.fulltext = []
        self.relationDict = {}
        self.customFields = {}
        self.createTimeStamp = None

        # Try our data sources, order matters
        self.__workflow()

        # Some defaults if the above failed
        if self.title is None:
           self.title = "New Dataset"
        if self.formatList == []:
            source = self.object.getPayload(self.packagePid)
            self.formatList.append(source.getContentType())

        # Index our metadata finally
        self.utils.add(self.index, "dc_title", self.title)
        if self.dcType is not None:
            self.utils.add(self.index, "dc_type", self.dcType)
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
        if self.createTimeStamp is None:
            self.utils.add(self.index, "create_timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime()))        
        self.params.setProperty("date_object_modified", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime()) )        
        self.utils.add(self.index, "date_object_modified", self.params.getProperty("date_object_modified"))
        self.utils.add(self.index, "date_object_created", self.params.getProperty("date_object_created"))

    def __workflow(self):
        # Workflow data
        WORKFLOW_ID = self.config.getString(None, ["workflow-id"])
        wfChanged = False
        workflow_security = []
        self.message_list = None
        stages = self.config.getJsonSimpleList(["stages"])
        pageTitle = self.config.getString(None, ["page-title"])
        displayType = self.config.getString("package-service", ["display-type"])
        initialStep = 0
        try:
            wfMeta = self.__getJsonPayload("workflow.metadata")
            wfMeta.getJsonObject().put("pageTitle", pageTitle)

            # Are we indexing because of a workflow progression?
            targetStep = wfMeta.getString(None, ["targetStep"])
            if targetStep is not None and targetStep != wfMeta.getString(None, ["step"]):
                wfChanged = True
                # Step change
                wfMeta.getJsonObject().put("step", targetStep)
                wfMeta.getJsonObject().remove("targetStep")
            # This must be a re-index then
            else:
                targetStep = wfMeta.getString(None, ["step"])

            # Security change
            for stage in stages:
                if stage.getString(None, ["name"]) == targetStep:
                    wfMeta.getJsonObject().put("label", stage.getString(None, ["label"]))
                    self.item_security = stage.getStringList(["visibility"])
                    workflow_security = stage.getStringList(["security"])
                    if wfChanged == True:
                        self.message_list = stage.getStringList(["message"])
        except StorageException:
            # No workflow payload, time to create
            initialStage = stages.get(initialStep).getString(None, ["name"])
            wfChanged = True
            wfMeta = JsonSimple()
            wfMetaObj = wfMeta.getJsonObject()
            wfMetaObj.put("id", WORKFLOW_ID)
            wfMetaObj.put("step", initialStage)
            wfMetaObj.put("pageTitle", pageTitle)
            stages = self.config.getJsonSimpleList(["stages"])
            for stage in stages:
                if stage.getString(None, ["name"]) == initialStage:
                    wfMetaObj.put("label", stage.getString(None, ["label"]))
                    self.item_security = stage.getStringList(["visibility"])
                    workflow_security = stage.getStringList(["security"])
                    self.message_list = stage.getStringList(["message"])

        # Has the workflow metadata changed?
        if wfChanged == True:
            inStream = IOUtils.toInputStream(wfMeta.toString(True), "UTF-8")
            try:
                StorageUtils.createOrUpdatePayload(self.object, "workflow.metadata", inStream)
            except StorageException:
                print " ERROR updating dataset payload"

        # Form processing
        coreFields = ["title", "description", "manifest", "metaList", "relationships", "responses"]
        formData = wfMeta.getObject(["formData"])
        if formData is not None:
            formData = JsonSimple(formData)
            # Core fields
            description = formData.getStringList(["description"])
            if description:
                self.descriptionList = description
            # Non-core fields
            data = formData.getJsonObject()
            for field in data.keySet():
                if field not in coreFields:
                    self.customFields[field] = formData.getStringList([field])

        # Manifest processing (formData not present in wfMeta)
        manifest = self.__getJsonPayload(self.packagePid)
        formTitles = manifest.getStringList(["title"])
        if formTitles:
            for formTitle in formTitles:
                if self.title is None:
                    self.title = formTitle
                    
        self.descriptionList = [manifest.getString("", ["description"])]
        formData = manifest.getJsonObject()
        for field in formData.keySet():
            if field == 'user_id':
                self.user_id = formData.get(field) # transitional info: save for mapping it to assign owner 
            elif field not in coreFields:
                value = formData.get(field)
                if value is not None and hasattr(value, 'strip') and value.strip() != "":
                    self.utils.add(self.index, field, value)
                    if field == "dc:title":
                        self.title = value
                    # We want to sort by date of creation, so it
                    # needs to be indexed as a date (ie. 'date_*')
                    if field == "dc:created":
                        parsedTime = time.strptime(value, "%Y-%m-%d")   
                        solrTime = time.strftime("%Y-%m-%dT%H:%M:%SZ", parsedTime)
                        self.utils.add(self.index, "date_created", solrTime)
                    elif field == "create_timestamp":
                        self.createTimeStamp = value
                        self.utils.add(self.index, "create_timestamp", value)
                    # try to extract some common fields for faceting
                    if field.startswith("dc:") and \
                            not (field.endswith(".dc:identifier.rdf:PlainLiteral") \
                              or field.endswith(".dc:identifier") \
                              or field.endswith(".rdf:resource")):
                        # index dublin core fields for faceting
                        basicField = field.replace("dc:", "dc_")
                        dot = field.find(".")
                        if dot > 0:
                            facetField = basicField[:dot]
                        else:
                            facetField = basicField
                        #print "Indexing DC field '%s':'%s'" % (field, facetField)
                        if facetField == "dc_title":
                            if self.title is None:
                                self.title = value
                        elif facetField == "dc_type":
                            if self.dcType is None:
                                self.dcType = value
                        elif facetField == "dc_creator":
                            if basicField.endswith("foaf_name"):
                                self.utils.add(self.index, "dc_creator", value)
                        else:
                            self.utils.add(self.index, facetField, value)
                        # index keywords for lookup
                        if field.startswith("dc:subject.vivo:keyword."):
                            self.utils.add(self.index, "keywords", value)

        self.utils.add(self.index, "display_type", displayType)

        # Workflow processing
        wfStep = wfMeta.getString(None, ["step"])
        self.utils.add(self.index, "workflow_id", wfMeta.getString(None, ["id"]))
        self.utils.add(self.index, "workflow_step", wfStep)
        self.utils.add(self.index, "workflow_step_label", wfMeta.getString(None, ["label"]))
        for group in workflow_security:
            self.utils.add(self.index, "workflow_security", group)

        # set OAI-PMH status to deleted
        if wfStep == "retired":
            self.utils.add(self.index, "oai_deleted", "true")

    def __messages(self):
        if self.message_list is not None and len(self.message_list) > 0:
            msg = JsonSimple()
            msg.getJsonObject().put("oid", self.oid)
            message = msg.toString()
            for target in self.message_list:
                self.utils.sendMessage(target, message)

    def __getJsonPayload(self, pid):
        payload = self.object.getPayload(pid)
        json = self.utils.getJsonObject(payload.open())
        payload.close()
        return json
    
    def __getUser(self):
        self.log.debug("baserule.py: Assign ownership: mapping id to user")
        
        mapConfig = self.config.getObject(["user-assignment"])
        if mapConfig is None:
            self.log.debug("baserule.py: no configuration has been set for mapping id to user.")
            return None

        uname = None
        try:
            userAssignment = JsonSimple(mapConfig)
            self.log.debug("baserule.py: user_id to user mapping configuration")
    
            modulePath = userAssignment.getString(None, ["module-path"])
            self.log.debug("baserule.py: module-path = {}", modulePath)
            
            className = userAssignment.getString(None, ["class-name"])
            self.log.debug("baserule.py: className = {}", className)
            
            initParams = userAssignment.getArray(["init-params"])
            self.log.debug("baserule.py: init-params (list) = {}", ' ,'.join(initParams))
            
            actionMethodName = userAssignment.getString(None, ["action-method-name"])
            self.log.debug("baserule.py: action-method-name = {}", actionMethodName)
            
            # JsonArray
            actionMethodParams = userAssignment.getArray(["action-method-params"])
      
            # This block may be used to mapping method params to internal variables?    
            try:
                self.log.debug("baserule.py: read parameters from tfpackage.")
                params = self.__getItems(actionMethodParams)
            except Exception, e:
                self.log.debug("baserule.py: read parameters failed. Reason: {}", str(e))
            
            if params is None or len(params) == 0:
                self.log.debug("baserule.py: read parameters returned None. Cannot carry on.")
                return None
                
            lookupPk = imp.load_source('', modulePath)
            lookupClass = getattr(lookupPk, className)
            lookupObj = lookupClass(*initParams)
            lookupMethod = getattr(lookupObj, actionMethodName)
            uname = lookupMethod(*params)
            
            self.log.debug("baserule.py: external lookup module returns: {}", uname)
        except Exception, e:
            self.log.debug("baserule.py: Cannot call user lookup module. More: {}", str(e))
        
        if (uname is None): # if mapping is successful, return real owner
            self.log.debug("baserule.py: did not map correctly, return None")
            return None
        else: # otherwise, assign admin as the owner
            self.log.debug("baserule.py: mapped successfully, return owner: '{}'", uname)
            return uname
        
    def __getItems(self, itemList):
        manifest = self.__getJsonPayload(self.packagePid).getJsonObject()
        params = []
        try:
            for field in itemList:
                self.log.debug("baserule.py: field in mapping params asking list: {}", field)
                v = manifest.get(field)
                if v is None:
                    raise KeyError("baserule.py: invalid field name:" + field)
                params.append(v)
            
#             for field in manifest.keySet():    
#                 self.log.debug("baserule.py: field in tfpackage: {} and its value = {}", field, manifest.get(field))
            return params    
        except Exception, e:
            return None            
