#
# Rules file for RDA Collections, blended with standard ReDBox logic for workflows
#
import time

from com.googlecode.fascinator.api.storage import StorageException
from com.googlecode.fascinator.common import JsonObject
from com.googlecode.fascinator.common import JsonSimple
from com.googlecode.fascinator.common.storage import StorageUtils

from java.lang import Exception
from java.lang import String
from java.util import HashSet

from org.apache.commons.io import IOUtils

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
        self.redboxVersion = self.config.getString("", "redbox.version.string")

        # Common data
        self.__newDoc()
        self.packagePid = None
        pidList = self.object.getPayloadIdList()
        for pid in pidList:
            if pid.endswith(".tfpackage"):
                self.packagePid = pid

        # Real metadata
        if self.itemType == "object":
            # Keep RDA's original RIF-CS
            try:
                self.__backupOriginal()
            except Exception, e:
                raise Exception("Unable to backup original RIF-CS from RDA: ", e)
            self.__basicData()
            self.__metadata()

        # Make sure security comes after workflows
        self.__security()

    def __backupOriginal(self):
        try:
            # This will throw an exception if the backup doesn't exist
            self.object.getPayload("rif.rda.xml")
        except Exception:
            try:
                # Grab the original from storage
                originalPayload = self.object.getPayload("rif.xml")
                inStream = originalPayload.open()
                try:
                    self.object.createStoredPayload("rif.rda.xml", inStream)
                except StorageException, e:
                    self.log.error("Error creating 'rif.rda.xml' payload for object '{}'", self.oid, e)
                    raise Exception("Error creating RIF-CS backup payload!", e)
            except Exception, e:
                self.log.error("Error accessing RIF-CS payload!", e)
                raise Exception("Error accessing RIF-CS payload!", e)

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
        self.utils.add(self.index, "harvest_rules", self.params.getProperty("rulesOid"))

        self.item_security = []
        self.owner = self.params.getProperty("owner", "admin")

    def __updateMetadataPayload(self, data):
        # Get and parse
        payload = self.object.getPayload("formData.tfpackage")
        json = JsonSimple(payload.open())
        payload.close()

        # Basic test for a mandatory field
        title = json.getString(None, ["dc:title"])
        if title is not None:
            # We've done this before
            return

        # Merge
        json.getJsonObject().putAll(data)

        # Store it
        inStream = IOUtils.toInputStream(json.toString(True), "UTF-8")
        try:
            self.object.updatePayload("formData.tfpackage", inStream)
        except StorageException, e:
            self.log.error("Error updating 'formData.tfpackage' payload for object '{}'", self.oid, e)

    def __checkMetadataPayload(self):
        try:
            # Simple check for its existance
            self.object.getPayload("formData.tfpackage")
            self.firstHarvest = False
        except Exception:
            self.firstHarvest = True
            # We need to create it
            self.log.info("Creating 'formData.tfpackage' payload for object '{}'", self.oid)
            # Prep data
            data = {
                "viewId": "default",
                "workflow_source": "RDA Legacy Import",
                "packageType": "dataset",
                "redbox:formVersion": self.redboxVersion,
                "redbox:newForm": "true"
            }
            package = JsonSimple(JsonObject(data))
            # Store it
            inStream = IOUtils.toInputStream(package.toString(True), "UTF-8")
            try:
                self.object.createStoredPayload("formData.tfpackage", inStream)
                self.packagePid = "formData.tfpackage"
            except StorageException, e:
                self.log.error("Error creating 'formData.tfpackage' payload for object '{}'", self.oid, e)
                raise Exception("Error creating package payload: ", e)

    def __storeIdentifier(self, identifier):
        try:
            # Where do we find persistent IDs?
            pidProperty = self.config.getString("persistentId", ["curation", "pidProperty"])
            metadata = self.object.getMetadata()
            storedId = metadata.getProperty(pidProperty)
            if storedId is None:
                metadata.setProperty(pidProperty, identifier)
                # Make sure the indexer triggers a metadata save afterwards
                self.params["objectRequiresClose"] = "true"
        except Exception, e:
            self.log.info("Error storing identifier against object: ", e)

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

    def __getRifPayload(self):
        try:
            # Need to make sure we retrieve the backed up RDA version,
            #  not the 'rif.xml' payload that we render ourselves
            payload = self.object.getPayload("rif.rda.xml")
            return payload
        except Exception:
            self.log.error("Payload 'rif.rda.xml' not found in object '{}'.", self.oid)
            return None

    def __indexList(self, name, values):
        # convert to set so no duplicate values
        for value in HashSet(values):
            self.utils.add(self.index, name, value)

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

        self.__checkMetadataPayload()
        self.__xmlParse()
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

    def __xmlParse(self):
        self.utils.registerNamespace("rif", "http://ands.org.au/standards/rif-cs/registryObjects")
        self.utils.registerNamespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

        if self.firstHarvest:
            self.utils.add(self.index, "workflow_source", "RDA Legacy Import")

        rifPayload = self.__getRifPayload()
        if rifPayload is None:
            self.log.error("Error accessing RIF-CS in storage: '{}'", self.oid)
            self.__indexError()
            return
        try:
            rif = self.utils.getXmlDocument(rifPayload.open())
            rifPayload.close()
        except Exception, e:
            self.log.error("Error parsing XML '{}' not accessible", self.oid, e)
            self.__indexError()
            return

        # RIF-CS version
        rif_string = self.__getSingleEntry(rif, "//rif:registryObjects/@xsi:schemaLocation")
        if rif_string is None:
            self.utils.add(self.index, "rifcsVersion", "error")
        else:
            if rif_string.find("rifcs/1.3") != -1:
                self.utils.add(self.index, "rifcsVersion", "1.3")
            else:
                if rif_string.find("rifcs/1.2") != -1:
                    self.utils.add(self.index, "rifcsVersion", "1.2")
                else:
                    self.utils.add(self.index, "rifcsVersion", "unknown")

        # RIF-CS object class
        rif_class = self.__getSingleEntry(rif, "//rif:registryObject/rif:collection/@type")
        if rif_class is None:
            rif_class = "non-collection"
        self.utils.add(self.index, "rif_class", rif_class)

        # Required - common
        self.__indexMandatory(rif, "//rif:registryObject/@group", "institution")
        self.__indexMandatory(rif, "//rif:registryObject/rif:originatingSource", "source")        
        identifier  = self.__indexMandatory(rif, "//rif:registryObject/rif:key", "dc_identifier")
        self.utils.add(self.index, "known_ids", identifier)
        self.__storeIdentifier(identifier)

        # Non-Collections stop here
        if rif_class == "non-collection":
            return False

        ###################################################
        #
        #  => XML Mapped to form data below here
        #       \/    \/    \/    \/    \/
        ###################################################
        # Grab as much meaningful data as we can from the RIF-CS
        data = {}
        self.notes = 0
        # Title + Description
        self.__store(data, "dc:title", rif, "//rif:registryObject/rif:collection/rif:name[@type='primary'][1]/rif:namePart[1]", "//rif:registryObject/rif:collection/rif:name[1]/rif:namePart[1]")
        data["title"] =  data["dc:title"]
        self.__store(data, "dc:description", rif, "//rif:registryObject/rif:collection/rif:description[@type='full']", "//rif:registryObject/rif:collection/rif:description[@type='brief']")
        data["description"] =  data["dc:description"]

        # Collection attributes
        self.__store(data, "dc:type.rdf:PlainLiteral", rif, "//rif:registryObject/rif:collection/@type", None)
        self.__store(data, "dc:modified", rif, "//rif:registryObject/rif:collection/@dateModified", None)
        self.__store(data, "dc:created", rif, "//rif:registryObject/rif:collection/@dateAccessioned", None)

        # Identifier
        idNodes = rif.selectNodes("//rif:registryObject/rif:collection/rif:identifier")
        if idNodes is not None and not idNodes.isEmpty():
            for idNode in idNodes:
                text = idNode.getText()
                type = self.__getSingleEntry(idNode, "@type")
                # The ID used as the RIF-CS key goes in the form data
                if identifier == text:
                    data["dc:identifier.rdf:PlainLiteral"] =  text
                    data["dc:identifier.dc:type.rdf:PlainLiteral"] =  type
                # The rest go in as notes
                else:
                    self.__addNote(data, "Additional ID Found: '%s' ('%s')" % (text, type))

        # URL(s)
        urlList = self.__getMultipleEntries(rif, "//rif:registryObject/rif:collection/rif:location/rif:address/rif:electronic[@type='url']/rif:value")
        count = 0
        for url in urlList:
            count += 1
            data["bibo:Website.%s.dc:identifier" % (count)] = url

        # Coverage - Spatial
        geoNodes = rif.selectNodes("//rif:registryObject/rif:collection/rif:coverage/rif:spatial")
        if geoNodes is not None and not geoNodes.isEmpty():
            count = 0
            for geoNode in geoNodes:
                count += 1
                data["dc:coverage.vivo:GeographicLocation.%s.rdf:PlainLiteral" % (count)] = geoNode.getText()
                self.__store(data, "dc:coverage.vivo:GeographicLocation.%s.dc:type" % (count), geoNode, "@type", None)
        # Coverage - Temporal
        self.__store(data, "dc:coverage.vivo:DateTimeInterval.vivo:start", rif, "//rif:registryObject/rif:collection/rif:coverage/rif:temporal[1]/rif:date[@type='dateTo']", None)
        self.__store(data, "dc:coverage.vivo:DateTimeInterval.vivo:end", rif, "//rif:registryObject/rif:collection/rif:coverage/rif:temporal[1]/rif:date[@type='dateFrom']", None)

        # Relations
        relatedNodes = rif.selectNodes("//rif:registryObject/rif:collection/rif:relatedObject")
        if relatedNodes is not None and not relatedNodes.isEmpty():
            for relatedNode in relatedNodes:
                key = self.__getSingleEntry(relatedNode, "rif:key")
                type = self.__getSingleEntry(relatedNode, "rif:relation/@type")
                label = self.__getSingleEntry(relatedNode, "rif:relation/rif:description")
                # Linked data is imported as notes for data etry staff to sort out.
                if label is not None:
                    self.__addNote(data, "Imported 'relatedObject': '%s' = '%s' ('%s')" % (key, type, label))
                else:
                    self.__addNote(data, "Imported 'relatedObject': '%s' = '%s'" % (key, type))

        # Related Info - Publications
        relInfoNodes = rif.selectNodes("//rif:registryObject/rif:collection/rif:relatedInfo[@type='publication']")
        if relInfoNodes is not None and not relInfoNodes.isEmpty():
            count = 0
            for relInfoNode in relInfoNodes:
                count += 1
                self.__store(data, "dc:relation.swrc:Publication.%s.dc:identifier" % (count), relInfoNode, "rif:identifier", None)
                self.__store(data, "dc:relation.swrc:Publication.%s.dc:title" % (count), relInfoNode, "rif:title", None)
                self.__store(data, "dc:relation.swrc:Publication.%s.skos:note" % (count), relInfoNode, "rif:notes", None)
        # Related Info - Websites
        relInfoNodes = rif.selectNodes("//rif:registryObject/rif:collection/rif:relatedInfo[@type='website']")
        if relInfoNodes is not None and not relInfoNodes.isEmpty():
            count = 0
            for relInfoNode in relInfoNodes:
                count += 1
                self.__store(data, "dc:relation.bibo:Website.%s.dc:identifier" % (count), relInfoNode, "rif:identifier", None)
                self.__store(data, "dc:relation.bibo:Website.%s.dc:title" % (count), relInfoNode, "rif:title", None)
                self.__store(data, "dc:relation.bibo:Website.%s.skos:note" % (count), relInfoNode, "rif:notes", None)

        # Subjects
        subjectNodes = rif.selectNodes("//rif:registryObject/rif:collection/rif:subject")
        if subjectNodes is not None and not subjectNodes.isEmpty():
            count = 0
            for subjectNode in subjectNodes:
                text = subjectNode.getText()
                type = self.__getSingleEntry(subjectNode, "@type")
                if type.startswith("anzsrc"):
                    # ANZSRC Codes... need data entry staff to get linked data versions
                    self.__addNote(data, "Imported ANZSRC Code: '%s' => '%s'" % (type, text))
                else:
                    # Keywords
                    count += 1
                    data["dc:subject.vivo:keyword.%s.rdf:PlainLiteral" % (count)] = text

        # Access Rights
        self.__store(data, "dc:accessRights.rdf:PlainLiteral", rif, "//rif:registryObject/rif:collection/rif:description[@type='accessRights']", None)
        # Rights or license(s)... RIF-CS v1.2
        rightsNodes = rif.selectNodes("//rif:registryObject/rif:collection/rif:description[@type='rights']")
        if rightsNodes is not None and not rightsNodes.isEmpty():
            count = 0
            for rightsNode in rightsNodes:
                text = rightsNode.getText()
                self.__addNote(data, "Imported Rights/Licence: '%s'" % (text))
        ###################################################
        #       /\    /\    /\    /\    /\
        #  => XML Mapped to form data above here
        #
        ###################################################
        self.__updateMetadataPayload(data)

    def __addNote(self, data, message):
        self.notes += 1
        noteField = "skos:note.%s.dc:description" % (self.notes)
        data[noteField] = message

    def __store(self, dictionary, key, document, xpath, fallbackXPath):
        # Try for our preferred path
        data = self.__getSingleEntry(document, xpath)
        if data is not None:
            dictionary[key] = data
        # or try again... if a fallback has been provided
        else:
            if fallbackXPath is not None:
                data = self.__getSingleEntry(document, fallbackXPath)
                if data is not None:
                    dictionary[key] = data

    def __workflow(self):
        # Workflow data
        WORKFLOW_ID = "dataset"
        wfChanged = False
        workflow_security = []
        self.message_list = None
        stages = self.config.getJsonSimpleList(["stages"])
        if self.owner == "guest":
            pageTitle = "Submission Request"
            displayType = "submission-request"
            initialStep = 0
        else:
            pageTitle = "Metadata Record"
            displayType = "package-dataset"
            initialStep = 1
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
            if field not in coreFields:
                value = formData.get(field)
                if value is not None and value.strip() != "":
                    self.utils.add(self.index, field, value)
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
            if self.owner is not None:
                self.utils.add(self.index, "workflow_security", self.owner)
        # set OAI-PMH status to deleted
        if wfStep == "retired":
            self.utils.add(self.index, "oai_deleted", "true")

    def __indexOptional(self, document, xPath, solrField):
        data = self.__getSingleEntry(document, xPath)
        if data is not None:
            self.utils.add(self.index, solrField, data)
            return data
        return None

    def __indexMandatory(self, document, xPath, solrField):
        data = self.__getSingleEntry(document, xPath)
        if data is None:
            self.log.error("Error indexing '{}' ('{}'). None found '{}'!", [solrField, xPath, self.oid])
            self.utils.add(self.index, solrField, "error")
            return "error"
        else:
            self.utils.add(self.index, solrField, data)
            return data

    def __getMultipleEntries(self, document, xPath):
        list = document.selectNodes(xPath)
        if list is None or list.isEmpty():
            return []
        else:
            result = []
            for entry in list:
                result.append(String(entry.getText()).trim())
            return result

    def __getSingleEntry(self, document, xPath):
        list = document.selectNodes(xPath)
        if list is None or list.isEmpty():
            return None
        else:
            entry = list.get(0)
            if list.size() > 1:
                self.log.warn("Found {} entries ('{}'), only using the first", list.size(), xPath)
            return String(entry.getText()).trim()

    def __getMultipartName(self, node):
        # Honorific
        honorific  = self.__getSingleEntry(node, "//rif:namePart[@type='title'][1]")
        if honorific is not None:
            title = honorific + " "
        else:
            title = ""

        # Given name
        given  = self.__getSingleEntry(node, "//rif:namePart[@type='given'][1]")
        if given is None:
            return None
        title += given

        # Family name
        family = self.__getSingleEntry(node, "//rif:namePart[@type='family'][1]")
        if family is not None:
            title += " " + family

        return title

    def __indexError(self):
        title = "Unknown Title, object '%s'" % self.oid
        self.utils.add(self.index, "title", title)
        self.utils.add(self.index, "dc_title", title)
        description = "Error during harvest/index for item '%s'. Could not access metadata from storage." % self.oid
        self.utils.add(self.index, "description", description)
        self.utils.add(self.index, "dc_description", description)
        return

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

    def __getJsonPayload(self, pid):
        payload = self.object.getPayload(pid)
        json = self.utils.getJsonObject(payload.open())
        payload.close()
        return json
