#
# Rules script for sample Parties - People data
#
import time

class IndexData:
    def __init__(self):
        pass

    def __activate__(self, context):
        # Prepare variables
        self.index = context["fields"]
        self.indexer = context["indexer"]
        self.object = context["object"]
        self.payload = context["payload"]
        self.params = context["params"]
        self.utils = context["pyUtils"]
        self.config = context["jsonConfig"]
        self.log = context["log"]

        # Common data
        self.__newDoc()

        # Real metadata
        if self.itemType == "object":
            self.__basicData()
            self.__metadata()

        # Make sure security comes after workflows
        self.__security(self.oid, self.index)

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
        self.utils.add(self.index, "display_type", "parties_people")

        self.item_security = []
        
    def __basicData(self):
        self.utils.add(self.index, "repository_name", self.params["repository.name"])
        self.utils.add(self.index, "repository_type", self.params["repository.type"])
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
        self.utils.add(self.index, "oai_set", "Parties_People")
        # Publication
        published = self.params["published"]
        if published is not None:
            self.utils.add(self.index, "published", "true")
        # NLA Integration
        nlaReady = self.params["ready_for_nla"]
        if nlaReady is not None:
            self.utils.add(self.index, "ready_for_nla", "ready")
        nlaProperty = self.config.getString(None, ["curation", "nlaIntegration", "pidProperty"])
        if nlaProperty is not None:
            nlaId = self.params[nlaProperty]
            if nlaId is not None:
                self.utils.add(self.index, "known_ids", nlaId)
                self.utils.add(self.index, "nlaId", nlaId)

    def __metadata(self):
        jsonPayload = self.object.getPayload("metadata.json")
        json = self.utils.getJsonObject(jsonPayload.open())
        jsonPayload.close()
        
        metadata = json.getObject("metadata")
        self.utils.add(self.index, "dc_identifier", metadata.get("dc.identifier"))
        
        data = json.getObject("data")
        self.utils.add(self.index, "dc_title", "%s, %s" % (data.get("Family_Name"), data.get("Given_Name")))

        self.utils.add(self.index, "dc_description", data.get("Description"))
        self.utils.add(self.index, "dc_format", "application/x-mint-party-people")
        
        for key in data.keySet():
            data_value = data.get(key)
            try:
                self.utils.add(self.index, key, data_value)
            except TypeError:
                # Some of the fields may be arrays
                for element in data_value:
                    self.utils.add(self.index, key, element)

        # Known IDs
        idFields = ["ID", "URI", "NLA_Party_Identifier", "ResearcherID", "openID", "Personal_URI"]
        for field in idFields:
            if data.containsKey(field):
                value = data.get(field)
                if value != "":
                    self.utils.add(self.index, "known_ids", value)
        identifier = json.getString(None, ["metadata", "dc.identifier"])
        if identifier is not None:
            self.utils.add(self.index, "known_ids", identifier)

        # Primary group membership
        basicGroupId = data.get("Groups")[0]
        if basicGroupId is not None and basicGroupId != "":
            # Look through each relationship
            relationships = json.getArray("relationships")
            if relationships is not None:
                for relationship in relationships:
                    # Does it end with our basic group?
                    identifier = relationship.get("identifier")
                    if identifier is not None and identifier.endswith("/group/%s" % basicGroupId):
                        # We've found it, just check if it is curated yet
                        #################################
                        ## Fixes issue #58 - I haven't removed this code entirely since
                        ## this is a quick fix for now, but nowhere else in the system
                        ## currently looks for this value except the ReDBox lookups, so
                        ## it may warrant complete removal of much of this code.
                        #curatedPid = relationship.get("curatedPid")
                        #if curatedPid is not None and curatedPid != "":
                        #    self.utils.add(self.index, "primary_group_id", curatedPid)
                        #else:
                        #    self.utils.add(self.index, "primary_group_id", identifier)
                        #################################
                        self.utils.add(self.index, "primary_group_id", identifier)

    def __security(self, oid, index):
        roles = self.utils.getRolesWithAccess(oid)
        if roles is not None:
            for role in roles:
                self.utils.add(index, "security_filter", role)
        else:
            # Default to guest access if Null object returned
            schema = self.utils.getAccessSchema("derby");
            schema.setRecordId(oid)
            schema.set("role", "guest")
            self.utils.setAccessSchema(schema, "derby")
            self.utils.add(index, "security_filter", "guest")

    def __indexList(self, name, values):
        for value in values:
            self.utils.add(self.index, name, value)
