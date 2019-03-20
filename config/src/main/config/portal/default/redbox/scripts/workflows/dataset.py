from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.api.storage import PayloadType
from com.googlecode.fascinator.api.storage import StorageException
from com.googlecode.fascinator.common import FascinatorHome
from com.googlecode.fascinator.common import JsonObject
from com.googlecode.fascinator.common import JsonSimple
from com.googlecode.fascinator.common.messaging import MessagingServices
from com.googlecode.fascinator.common.solr import SolrResult
from com.googlecode.fascinator.messaging import TransactionManagerQueueConsumer
from com.googlecode.fascinator.portal.services import OwaspSanitizer
from java.io import ByteArrayInputStream
from java.io import ByteArrayOutputStream
from java.lang import Exception
from java.lang import String

from org.apache.commons.lang import StringEscapeUtils
from org.json.simple import JSONArray


class DatasetData:
    def __init__(self):
        self.messaging = MessagingServices.getInstance()

    def __activate__(self, context):
        self.velocityContext = context
        self.log = self.vc("log")
        ##self.log.debug("**** dataset.py")

        # We use these here in __activate__()
        formData = self.vc("formData")
        #print "context=%s" % formData
        #self.log.debug("formData: {}", repr(formData))
        response = self.vc("response")
        request = self.vc("request")
        func = formData.get("func", "")
        id = formData.get("id")
        # This needs to remain None unless an AJAX event is happening
        result = None

        # We need these later
        self.__formData = formData
        self.isAjax = bool(formData.get("ajax"))
        self.__object = None
        self.__oid = formData.get("_oid") or formData.get("oid")
        self.Services = self.vc("Services")
        self.page = self.vc("page")



        # These cache responses from methods
        self.__manifest = None
        self.__solrMetadata = None
        self.__tfpackage = None
        self.__wfMetadata = None

        # Allow for URL GET paramters
        if self.vc("request").method == "GET" and func != "":
            func = ""
        if func == "" and request.getParameter("func"):
            func = request.getParameter("func")

        config = self._getDataConfig()
        self.presentationConfig = config.getObject("presentation-settings")


        self.log.debug("func='%s', oid='%s', id='%s'" % (func, self.__oid, id))
        try:
            if func == "file-upload":
                ##self.log.debug("**************\n  file-upload\n**************")
                result = JsonObject()
                result.put("ok", "file-upload")
                result.put("oid", self.__oid)

            # If we have an OID, ensure our data is accessible first
            if self.__oid is not None:
                # Are we updating the package whilst here?
                if func == "update-package-meta":
                    result = JsonObject()
                    result = self._updatePackageMetadata()
                elif func == "update-package-meta-deposit":
                    result = JsonObject()
                    result = self._updatePackageMetadata(True)

        except Exception, e:
            self.log.error("Failed to load manifest", e)
            result = JsonObject()
            result.put("status", "error")
            result.put("message", str(e))

        # Close our object... if we update properties this triggers a save
        if self.__object is not None:
            self.__object.close()
            self.__object=None

        if result is not None:
            writer = response.getPrintWriter("text/plain; charset=UTF-8")
            writer.println(result.toString())
            writer.close()



    # Get from velocity context
    def vc(self, index):
        if self.velocityContext[index] is not None:
            return self.velocityContext[index]
        else:
            self.log.error("ERROR: Requested context entry '" + index + "' doesn't exist")
            return None

    # Some basic wrappers to long calls
    def userRoles(self):
        return self.vc("page").authentication.get_roles_list()

    def username(self):
        return self.vc("page").authentication.get_username()

    def getCurrentStep(self):
        return self._getWorkflowMetadata().getString("", ["step"])

    def getCurrentStepLabel(self):
        return self._getWorkflowMetadata().getString("", ["label"])

    ### Supports form rendering, not involved in AJAX
    def getHandleUri(self):
        pid = None
        pidProperty = self.vc("systemConfig").getString(None, ["curation", "pidProperty"])
        if pidProperty is None:
            self.log.error("No configuration found for persistent IDs!")
        else:
            try:
                pid = self._getObject().getMetadata().getProperty(pidProperty)
                #self.log.info("****Persistent ID = '{}'", pidProperty)
            except Exception,e:
                self.log.warn("Failed to get Persistent ID from storage!", e)
        return pid or ""

    def getDoiMetadata(self):
        propName = self.vc("systemConfig").getString(None, ["andsDoi", "doiProperty"])
        try:
            doi = self._getObject().getMetadata().getProperty(propName)
            self.log.debug("Getting DOI from storage = '{}'", doi)
        except Exception,e:
            self.log.error("Failed to get DOI from storage!", e)
            return "{\"error\": \"Error accessing DOI in storage, please see system logs.\"}"

        if doi is not None:
            return "{\"doi\": \""+doi+"\"}"
        else:
            return "{}"

    ### Supports form rendering, not involved in AJAX
    def getNextStepAcceptMessage(self):
        step = self.getCurrentStep()
        msg = "?"
        if step == "inbox":
            msg = "This record is ready for the '''Investigation''' stage."
        elif step == "investigation":
            msg = "This record is ready for the '''Metadata Review''' stage."
        elif step == "metadata-review":
            msg = "This record is ready for the '''Final Review''' stage."
        elif step == "final-review":
            msg = "This record is ready to be '''Published'''."
        elif step == "live":
            msg = "This record has already been '''Published'''."
        elif step == "retired":
            msg = "This record has been '''Retired'''."
        return msg

    ### Supports form rendering, not involved in AJAX
    def getNextStepAcceptValidationErrorMessage(self):
        step = self.getCurrentStep()
        msg = "?"
        if step == "pending":
            msg = "You must accept responsibility and accountability for the" + \
            " accuracy and completeness of the information provided before" + \
            " you can submit this item!"
        elif step == "reviewing":
            msg = "You must check the 'Make record live' checkbox!"
        elif step == "live":
            msg = "[Live]"
        return msg

    ### Supports form rendering, not involved in AJAX
    def getJsonMetadata(self):
        package = self._getTFPackage()
        # ensure sanitization occurs
        OwaspSanitizer.sanitizeTfPackage(package)
        self.log.debug("package after sanitized is: %s" % package)
        ## Look for a title
        title = package.getString("", ["dc:title"])
        title = package.getString(title, ["title"])
        ## And a description
        description = package.getString("", ["dc:abstract"])
        description = package.getString(description, ["description"])
        ## Make sure we have the fields we need
        json = package.getJsonObject()
        json.put("dc:title", title)
        json.put("dc:abstract", description)
        ## fix newlines
        ignoreFields = ["metaList", "relationships", "responses"]
        for key in json:
            if key not in ignoreFields:
                value = json.get(key)
                if value and value.find("\n"):
                    value = value.replace("\n", "\\n")
                    json.put(key, value)
                    ##self.log.info("****** %s=%s" % (key,value))
        jsonStr = package.toString(True)
        ##self.log.info(" ******** jsonStr: %s" % jsonStr)
        return jsonStr

    ### Supports form rendering, not involved in AJAX
    def getAttachedFiles(self):
        # Build a query
        req = SearchRequest("attached_to:%s" % self.__oid)
        req.setParam("rows", "1000")
        # Run a search
        out = ByteArrayOutputStream()
        self.Services.getIndexer().search(req, out)
        result = SolrResult(ByteArrayInputStream(out.toByteArray()))
        # Process results
        docs = JSONArray()
        for doc in result.getResults():
            entry = JsonObject()
            entry.put("filename",        doc.getFirst("filename"))
            entry.put("attachment_type", doc.getFirst("attachment_type"))
            entry.put("access_rights",   doc.getFirst("access_rights"))
            entry.put("oid",             doc.getFirst("id"))
            docs.add(entry)
        return docs.toString()

    ### Supports form rendering, not involved in AJAX
    def getFormData(self, field):
        formData = self.vc("formData")
        #print "********** getFormData(field='%s')='%s'" % (field, formData)
        return StringEscapeUtils.escapeHtml(formData.get(field, ""))

    def getPresentationConfig(self, field):
        presentationConfig = self.presentationConfig
        #print "********** getPresentationConfig '%s'" % (presentationConfig.get(field) )
        if presentationConfig is None or presentationConfig.get(field) is None:
            return ''

        return StringEscapeUtils.escapeHtml(presentationConfig.get(field))

    ### Supports form rendering, not involved in AJAX
    def getOid(self):
        self.log.debug("getOid() = '{}'", self.__oid)
        return self.__oid

    # Retrieve and cache the current object
    def _getObject(self):
        if not self.__object:
            try:
                self.__object = self.Services.storage.getObject(self.__oid)
            except StorageException, e:
                self.log.error("Failed to retrieve object : ", e)
        return self.__object


    # Retrieve and parse the Fascinator Package from storage
    def _getTFPackage(self):
        if self.__tfpackage is None:
            payload = None
            inStream = None

            # We don't need to worry about close() calls here
            try:
                object = self._getObject()
                sourceId = object.getSourceId()
                payload = None
                if sourceId is None or not sourceId.endswith(".tfpackage"):
                    # The package is not the source... look for it
                    for pid in object.getPayloadIdList():
                        if pid.endswith(".tfpackage"):
                            payload = object.getPayload(pid)
                            payload.setType(PayloadType.Source)
                else:
                    payload = object.getPayload(sourceId)
                inStream = payload.open()
            except Exception, e:
                self.log.error("Error during package access", e)
                return None

            # The input stream has now been opened, it MUST be closed
            try:
                self.__tfpackage = JsonSimple(inStream)
            except Exception, e:
                self.log.error("Error parsing package contents", e)
            payload.close()
        return self.__tfpackage

    # Get the manifest from the Fascinator package and wrap in JSON Library
    def _getManifest(self):
        if self.__manifest is None:
            package = self._getTFPackage()
            if package is None:
                return None
            manifestJson = package.writeObject(["manifest"])
            self.__manifest = JsonSimple(manifestJson)
        return self.__manifest

    # Save the provided package to disk
    def _saveTFPackage(self, tfpackage):
        object = self._getObject()
        OwaspSanitizer.sanitizeTfPackage(tfpackage)
        self.log.trace("tfpackage after sanitized is: %s" % tfpackage)
        jsonString = String(tfpackage.toString(True))
        jsonData = jsonString.getBytes("UTF-8")
        self.packagePid = None
        pidList = self.__object.getPayloadIdList()
        for pid in pidList:
            if pid.endswith(".tfpackage"):
                self.packagePid = pid
        object.updatePayload(self.packagePid, ByteArrayInputStream(jsonData))

    # Save the current package
    def _savePackage(self):
        self._saveTFPackage(self._getTFPackage())

    # Get our object's workflow metadata from storage
    def _getWorkflowMetadata(self):
        if self.__wfMetadata is None:
            payload = None
            inStream = None

            # We don't need to worry about close() calls here
            try:
                object = self._getObject()
                payload = object.getPayload("workflow.metadata")
                inStream = payload.open()
            except Exception, e:
                self.log.error("Error during metadata access", e)
                return None

            # The input stream has now been opened, it MUST be closed
            try:
                self.__wfMetadata = JsonSimple(inStream)
            except Exception, e:
                self.log.error("Error during metadata access", e)
            payload.close()
        return self.__wfMetadata

    # Save the workflow metadata provided to disk
    def _saveWorkflowMetadata(self, wfMetadata):
        object = self._getObject()
        jsonString = String(wfMetadata.toString(True))
        jsonData = jsonString.getBytes("UTF-8")
        object.updatePayload("workflow.metadata", ByteArrayInputStream(jsonData))

    # Update and save the package metadata
    def _updatePackageMetadata(self, progressStep = False):
        result = JsonObject()
        self.log.debug("** dataset update-package-meta **")
        result.put("error", "unknown")

        currentStep = self.getCurrentStep()
        targetStep = None
        self.log.debug("  currentStep='%s'" % currentStep)

        # A security check
        try:
            # Find our workflow configuraion
            systemConfig = self.vc("systemConfig")
            jsonConfigFile = systemConfig.getObject(["portal", "packageTypes", "dataset"]).get("jsonconfig")
            jsonConfigFile = FascinatorHome.getPathFile(
                    "harvest/workflows/" + jsonConfigFile)
            config = JsonSimple()
            try:
                config = JsonSimple(jsonConfigFile)
            except:
                self.log.error("Error accessing config", e)
                result.put("error", "Error accessing config: '%s'" % str(e))
                return result
            stages = config.getJsonSimpleList(["stages"])

            # Currently indexed metadata
            solr = self.__getSolrData()
            if solr is None:
                result.put("error", "Solr document unavailable!")
                return result

            # Find were we are in the workflow
            currentStage = None
            nextStage = None
            nextStep = None
            for stage in stages:
                # This executes on loop AFTER we found current stage
                if currentStage is not None:
                    nextStage = stage
                    nextStep = nextStage.getString(None, ["name"])
                    break
                # Find the current stage
                stageName = stage.getString(None, ["name"])
                if stageName is not None and stageName == currentStep:
                    currentStage = stage

            # Get user data
            username = self.username()
            userRoles = self.userRoles()
            owner = solr.getFirst("owner")

            # Print some debug data
            #self.log.debug(" === username = '%s'" % username)
            #self.log.debug(" === userRoles = '%s'" % userRoles)
            #self.log.debug(" === nextStep = '%s'" % nextStep)
            #self.log.debug(" === owner = '%s'" % owner)

            # Now do the security check
            workflowSecurity = solr.getList("workflow_security")
            if workflowSecurity is None:
                # Use with care... this is no longer a Java List
                workflowSecurity = []
            if progressStep:
                targetStep = nextStep
                self.log.debug(" === targetStep = '%s'" % targetStep)
            # Let owners or admins user the 'pending' step
            if (currentStep == "pending") and (owner != username) and \
                    ("admin" not in userRoles):
                message = "Only the owner or admin can do this!"
                self.log.error(message)
                result.put("error", message)
                return result
            # Otherwise, normal workflow security applies, with admin always allowed
            else:
                if ("admin" not in userRoles) and \
                        (not set(userRoles).intersection(workflowSecurity)):
                    message = "Not an admin or you do not have the correct role"
                    self.log.error(message)
                    result.put("error", message)
                    return result
        except Exception, e:
            self.log.error("Error in _updatePackageMetadata():", e)
            result.put("error", str(e))
            return result

        # Update our data
        formData = self.__formData
        tfpackage = self._getTFPackage()
        packageJson = tfpackage.getJsonObject()
        try:
            # Update all of our data fields
            metaList = list(formData.getValues("metaList"))
            storedList = tfpackage.getStringList(["metaList"])
            if storedList is None:
                # Use with care... this is no longer a Java List
                storedList = []
            removedSet = set(storedList).difference(metaList)
            try:
                # Add the actual data
                for metaName in metaList:
                    value = formData.get(metaName)
                    packageJson.put(metaName, value)
                # We are overwriting this list
                tfMetaList = tfpackage.writeArray(["metaList"])
                tfMetaList.clear()
                tfMetaList.addAll(metaList)
                # Remove any old data
                for metaName in removedSet:
                    if metaName != "relationships":
                        packageJson.remove(metaName)
            except Exception, e:
                self.log.error("Error updating package data", e)
                result.put("error", "Error updating package data")
                return result

            # Copy core Fascinator data
            title = tfpackage.getString("", ["dc:title"])
            description = tfpackage.getString("", ["dc:description"])
            packageJson.put("title", title)
            packageJson.put("description", description)
            if not title:
                self.log.error("Object has no title!")
                result.put("error", "no title")
                return result

            # Update our worflow data
            try:
                wfMeta = self._getWorkflowMetadata()
                wfJson = wfMeta.getJsonObject()
                if targetStep is not None:
                    wfJson.put("targetStep", targetStep)

                self.log.debug("title = '%s'" % title)
                self.log.debug("wfMeta = '%s'" % wfMeta)

                formJson = wfMeta.writeObject(["formData"])
                formJson.put("title", title)
                formJson.put("description", description)
                self._saveWorkflowMetadata(wfMeta)
            except Exception, e:
                self.log.error("Error updating workflow data", e)

            # Save & re-index
            self._saveTFPackage(tfpackage)
            self._reIndex(targetStep)
            result.remove("error")
            result.put("ok", "updated ok")
            result.put("oid", self.__oid)
        except Exception, e:
            self.log.error("Error updating data", e)
            result.put("error", str(e))

        return result

    # Re-index the current object
    def _reIndex(self, step):
        object = self._getObject()
        oid = object.getId()

        # Notify the curation manager
        self.sendMessage(oid, step)

    # Get the solr document for this object
    def __getSolrData(self):
        if self.__solrMetadata is None:
            object = self._getObject()
            if object is None:
                return None
            oid = object.getId()

            try:
                # Build our query
                query = 'id:"%s"' % oid
                req = SearchRequest(query)
                req.addParam("fq", 'item_type:"object"')
                out = ByteArrayOutputStream()
                # Search and parse
                self.Services.getIndexer().search(req, out)
                result = SolrResult(ByteArrayInputStream(out.toByteArray()))
                # Check results
                if result.getNumFound() == 0:
                    self.log.error("No solr document found for OID: '{}'", oid)
                    return None
                if result.getNumFound() > 1:
                    self.log.warn("WARNING: Found {} solr documents for OID '{}', expected 0!", result.getNumFound(), oid)
                # The first result is all we care about
                self.__solrMetadata = result.getResults().get(0)
            except Exception, e:
                self.log.error("Error in __getSolrData(): ", e)
        return self.__solrMetadata

    # Send an event notification to the curation manager
    def sendMessage(self, oid, step):
        message = JsonObject()
        message.put("oid", oid)
        if step is None:
            message.put("eventType", "ReIndex")
        else:
            message.put("eventType", "NewStep : %s" % step)
            message.put("newStep", step)
        message.put("username", self.vc("page").authentication.get_username())
        message.put("context", "Workflow")
        message.put("task", "workflow")
        self.messaging.queueMessage(
                TransactionManagerQueueConsumer.LISTENER_ID,
                message.toString())

    def _getDataConfig(self):
        systemConfig = self.vc("systemConfig")

        jsonConfigFileString = systemConfig.getObject(["portal", "packageTypes", "dataset"]).get("jsonconfig")

        jsonConfigFile = FascinatorHome.getPathFile(
            "harvest/workflows/" + jsonConfigFileString)
        config = JsonSimple()
        config = JsonSimple(jsonConfigFile)

        return config

