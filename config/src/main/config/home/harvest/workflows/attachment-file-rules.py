from com.googlecode.fascinator.common import FascinatorHome
from com.googlecode.fascinator.common import JsonSimple

import sys
import time
pathToWorkflows = FascinatorHome.getPath("harvest/workflows")
if sys.path.count(pathToWorkflows) == 0:
    sys.path.append(pathToWorkflows)

class IndexData:
    def __activate__(self, context):
        try:
            # Prepare variables
            self.index = context["fields"]
            self.object = context["object"]
            self.payload = context["payload"]
            self.params = context["params"]
            self.utils = context["pyUtils"]
            self.config = context["jsonConfig"]
            self.log = context["log"]

            # Common data
            self.__newDoc() # sets: self.oid, self.pid, self.itemType
            self.item_security = []
            self.owner = self.params.getProperty("owner", "system")
            self.log.debug("Running attachment-file-rules.py... itemType='{}'", self.itemType)

            # Real metadata
            if self.itemType == "object":
                self.__index("repository_name", self.params["repository.name"])
                self.__index("repository_type", self.params["repository.type"])
                self.__index("workflow_source", self.params["workflow.source"])
                self.__metadata()

            # Make sure security comes after workflows
            self.__security()

        except Exception, e:
            self.log.error("ERROR indexing attachment: {}", e);

    def __index(self, name, value):
        self.utils.add(self.index, name, value)

    def __indexList(self, name, values):
        for value in values:
            self.utils.add(self.index, name, value)

    def __newDoc(self):
        self.oid = self.object.getId()
        self.pid = self.payload.getId()
        metadataPid = self.params.getProperty("metaPid", "DC")

        self.__index("storage_id", self.oid)
        if self.pid == metadataPid:
            self.itemType = "object"
        else:
            self.oid += "/" + self.pid
            self.itemType = "datastream"
            self.__index("identifier", self.pid)
        self.__index("id", self.oid)
        self.__index("item_type", self.itemType)
        self.__index("last_modified", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        self.__index("harvest_config", self.params.getProperty("jsonConfigOid"))
        self.__index("harvest_rules",  self.params.getProperty("rulesOid"))
        self.__index("display_type", "attachment")

    def __metadata(self):
        wfMeta = self.__getJsonPayload("attachments.metadata")
        if wfMeta is None:        
            self.log.debug("Without formdata...")
        else:            
            self.log.debug("Processing formdata...")
            try:
              self.log.debug("__metadata() wfMeta={}", wfMeta.toString(True))
              # Form processing
              formData = wfMeta.getObject(["formData"])
              if formData is not None:
                  for key in formData.keySet():
                      if key != "owner":
                          self.__index(key, formData.get(key))
                  filename = wfMeta.getString(None, ["formData", "filename"])
                  if filename is None:
                      self.log.warn("No filename for attachment!")
                      filename = "UNKNOWN"
                  self.__index("dc_title", "Attachment-%s" % filename)
                  #if wfMeta.getString("private", ["formData", "access_rights"]) == "public":
                  #    self.item_security.append("guest")
                  #    self.__index("workflow_security", "guest")
            except:
                self.log.warn("Form data not available.")

        # Security        
        self.item_security.append("admin")
        self.__index("workflow_security", "admin")
        

    def __getJsonPayload(self, pid):
        payload = None
        try:
            payload = self.object.getPayload(pid)
            json = JsonSimple(payload.open())
            payload.close()
            return json
        except:
            if payload is not None:
                try:
                    payload.close()
                except:
                    ## Wasn't open
                    pass
            return {}

    def __security(self):
        # Security
        roles = self.utils.getRolesWithAccess(self.oid)
        if roles is not None:
            # For every role currently with access
            for role in roles and len(roles):
                # Should show up, but during debugging we got a few
                if role != "":
                    if role in self.item_security:
                        # They still have access
                        self.__index("security_filter", role)
                    else:
                        # Their access has been revoked
                        self.__revokeAccess(role)
            # Now for every role that the new step allows access
            for role in self.item_security:
                if role not in roles:
                    # Grant access if new
                    self.__grantAccess(role)
                    self.__index("security_filter", role)
        # No existing security
        else:
            if self.item_security is None:
                # Guest access if none provided so far
                self.__grantAccess("guest")
                self.__index("security_filter", role)
            else:
                # Otherwise use workflow security
                for role in self.item_security:
                    # Grant access if new
                    self.__grantAccess(role)
                    self.__index("security_filter", role)
        # Ownership
        if self.owner is None:
            self.__index("owner", "system")
        else:
            self.__index("owner", self.owner)

    # TODO: get accesscontrol from system-config.json
    def __grantAccess(self, newRole):
        schema = self.utils.getAccessSchema("hibernateAccessControl");
        schema.setRecordId(self.oid)
        schema.set("role", newRole)
        self.utils.setAccessSchema(schema, "hibernateAccessControl")

    def __revokeAccess(self, oldRole):
        schema = self.utils.getAccessSchema("hibernateAccessControl");
        schema.setRecordId(self.oid)
        schema.set("role", oldRole)
        self.utils.removeAccessSchema(schema, "hibernateAccessControl")
