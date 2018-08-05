import re
import traceback
import os
from com.googlecode.fascinator.api.storage import StorageException
from com.googlecode.fascinator.common import JsonSimple
from java.io import ByteArrayInputStream
from java.lang import Exception
from java.lang import String
from org.apache.commons.lang import StringEscapeUtils
from org.apache.commons.lang import StringUtils
from org.joda.time import DateTime, DateTimeZone
from com.googlecode.fascinator.portal.services import OwaspSanitizer


class MigrateData:
    def __init__(self):
        self.packagePidSuffix = ".tfpackage"
        self.pdfSuffix = ".pdf"
        self.redboxVersion = None

    def __activate__(self, bindings):
        # Prepare variables
        self.systemConfig = bindings["systemConfig"]
        self.object = bindings["object"]
        self.log = bindings["log"]
        self.audit = bindings["auditMessages"]
        self.pidList = None
        self.pdfs = {}

        # Look at some data
        self.oid = self.object.getId()

        try:
            # # check if object creation and modification dates...
            self.insertCreateAndModifiedDate()
            #
            # # load the package data..
            self.__getPackageData()
            if self.packageData is not None:
                self.log.info(self.packageData.toString(True))
                # update the redbox version...
                self.updateVersion()

                self.createLinkedFile(self.pdfs)

                # # update description to wysiwyg descriptions and init for multiple descriptions
                self.setDescriptionShadow()

                # # check recordAsLocation config and, if true, set record as location
                self.setRecordAsLocation()

                # add access rights type if none exists, but relevant licence present
                self.updateRightsType()

                # add new keys if not present
                self.injectFreshKeys()

                # # save the package data...
                self.__savePackageData()

            self.object.close()
        except Exception, e:
            traceback.print_exc()
            self.object = None

    def insertCreateAndModifiedDate(self):
        # check if object created and modified date exists, populate with current date if not..
        propMetadata = self.object.getMetadata()
        now = DateTime().toString()
        self.log.debug("date time now is: %s" % now)
        localTimeZoneHrs = str(DateTime().toString("ZZ"))
        self.log.info("current zone hours is: %s" % localTimeZoneHrs)
        createdDateTime = str(propMetadata.getProperty("date_object_created"))
        self.log.debug("created date time was: %s" % createdDateTime)
        if createdDateTime is None:
            self.log.debug("Updating created time...")
            propMetadata.setProperty("date_object_created", now)
        elif createdDateTime.endswith("Z"):
            ## TODO : remove this temporary workaround to strip any UTC and replace with local timezone (for solr)
            createdDateTimeAsLocal = re.sub("Z+$", "", createdDateTime) + localTimeZoneHrs
            self.log.debug("updated created date time to: %s" % createdDateTimeAsLocal)
            propMetadata.setProperty("date_object_created", createdDateTimeAsLocal)
        else:
            self.log.debug("existing created time does not end in 'Z', so remains untouched.")
        modifiedDateTime = str(propMetadata.getProperty("date_object_modified"))
        self.log.debug("modified date time was: %s" % modifiedDateTime)
        if modifiedDateTime is None:
            self.log.debug("Updating modified time...")
            propMetadata.setProperty("date_object_modified", now)
        elif modifiedDateTime.endswith("Z"):
            ## TODO : remove this temporary workaround to strip any UTC and replace with local timezone (for solr)
            modifiedDateTimeAsLocal = re.sub("Z+$", "", modifiedDateTime) + localTimeZoneHrs
            self.log.debug("updated modified date time to: %s" % modifiedDateTimeAsLocal)
            propMetadata.setProperty("date_object_modified", modifiedDateTimeAsLocal)
        else:
            self.log.debug("existing modified time does not end in 'Z', so remains untouched.")


    def updateVersion(self):
        if self.redboxVersion is None:
            self.redboxVersion = self.systemConfig.getString(None, ["redbox.version.string"])
        if self.redboxVersion is None:
            self.log.error("Error, could not determine system version!")
            return
        self.getPackageJson().put("redbox:formVersion", self.redboxVersion)

    def setDescriptionShadow(self):
        deprecated_description = self.getPackageJson().get("dc:description")
        relevant_description = self.getPackageJson().get("dc:description.1.text")
        if self.getPackageJson().get("dc:description.0.text"):
            self.log.warn("Found current description for workflow initializer: 'dc:description.0.text'")
        if relevant_description:
            self.log.info(
                "Found current populated description for 'dc:description.1.text': %s, so skipping description migration..." % relevant_description)
            return
        else:
            ## no tags are added to wysiwyg until user interacts with wysiwyg editor
            unescapedDescription = ""
            escapedDescription = ""
            rawDescription = StringUtils.defaultString(deprecated_description)
            ## sanitize the incoming description
            self.log.debug("raw deprecated description is: %s" % rawDescription)
            sanitizedDescription = OwaspSanitizer.sanitizeHtml(rawDescription)
            if (sanitizedDescription):
                # not completely accurate for checking for tags but ensures a style consistent with wysiwyg editor
                if re.search("^<p>.*</p>|^&lt;p&gt;.*&lt;\/p&gt;", sanitizedDescription):
                    ## deprecated description may be unescaped or escaped already - so ensure both cases covered
                    unescapedDescription = StringEscapeUtils.unescapeHtml("%s" % sanitizedDescription)
                    escapedDescription = OwaspSanitizer.escapeHtml("%s" % sanitizedDescription)
                else:
                    unescapedDescription = StringEscapeUtils.unescapeHtml("<p>%s</p>" % sanitizedDescription)
                    escapedDescription = OwaspSanitizer.escapeHtml("<p>%s</p>" % sanitizedDescription)
            self.log.info("relevant unescaped description is: %s" % unescapedDescription)
            self.log.info("relevant escaped description is: %s" % escapedDescription)
            self.getPackageJson().put("dc:description.1.text", unescapedDescription)
            self.getPackageJson().put("dc:description.1.shadow", escapedDescription)
            self.getPackageJson().put("dc:description.1.type", "full")
            if self.getPackageJson().get("viewId") not in [ "dashboard" ]:
              self.log.debug("Removing deprecated 'dc:description' key...")
              self.getPackageJson().remove("dc:description")
            self.log.debug(
                "Completed migrating 'dc:description' %s to dc:description.1.text|shadow" % deprecated_description)

    def setRecordAsLocation(self):
        hasRecordAsLocationDefault = self.systemConfig.getString("", "rifcs", "recordAsLocation", "default")
        if hasRecordAsLocationDefault:
            recordAsLocationTemplate = self.systemConfig.getString("", "rifcs", "recordAsLocation", "template")
            self.log.debug("record as location template is %s" % recordAsLocationTemplate)
            urlBase = self.systemConfig.getString("", "urlBase")
            self.log.debug("url base is: %s" % urlBase)
            urlBasePattern = "\$\{urlBase\}"
            oidBasePattern = "\$\{oid\}"
            recordAsLocation = re.sub(urlBasePattern, urlBase, recordAsLocationTemplate)
            recordAsLocation = re.sub(oidBasePattern, self.oid, recordAsLocation)
            self.log.info("record as location is: %s" % recordAsLocation)
            self.getPackageJson().put("recordAsLocationDefault", recordAsLocation)
        else:
            self.log.info("record as location default is: %s," % hasRecordAsLocationDefault,
                          "so skipping 'record as location' migration...")

    def updateRightsType(self):
        accessRightsType = self.getPackageJson().get("dc:accessRightsType")
        self.log.debug("access rights: %s" % accessRightsType)
        ## because a user can deliberately change access rights type to "", ensure only change for null access rights types
        if accessRightsType is None:
            license = StringUtils.defaultString(self.getPackageJson().get("dc:license.skos:prefLabel"))
            self.log.info("License rights is: %s " % license)
            if re.search("CC|ODC|PDDL", str(license), re.IGNORECASE):
                self.getPackageJson().put("dc:accessRightsType", "open")
                self.log.debug("Added access rights type.")
            else:
                self.getPackageJson().put("dc:accessRightsType", "")
                self.log.debug("Added empty access rights type, because licence is: %s" % license)
        else:
            self.log.info(
                "Record already has access rights type key, with value: %s, so skipping update rights type migration." % accessRightsType)

    def injectFreshKeys(self):
        for freshKey in ["identifierText.1.creatorName.input", "pcName.identifierText",
                         "identifierText.1.supName.input",
                         "identifierText.1.collaboratorName.input"]:
            if self.getPackageJson().get(freshKey) is None:
                self.getPackageJson().put(freshKey, "")
                self.log.debug("added fresh key: %s" % freshKey)
            else:
                self.log.info("skipping fresh key: %s as it already exists" % freshKey)

    def getPackageJson(self):
        return self.packageData.getJsonObject()

    def __getPackageData(self):
        # Find our package payload
        self.packagePid = None
        self.packageData = None
        try:
            self.pidList = self.object.getPayloadIdList()
            for pid in self.pidList:
                if pid.endswith(self.packagePidSuffix):
                    self.packagePid = pid
                self.collectWhitespacePdfs(pid)
        except StorageException:
            self.log.error("Error accessing object PID list for object '{}' ", self.oid)
            return
        if self.packagePid is None:
            self.log.debug("Object '{}' has no package data", self.oid)
            return

        # Retrieve our package data

        try:
            payload = self.object.getPayload(self.packagePid)
            try:
                self.packageData = JsonSimple(payload.open())
            except Exception:
                self.log.error("Error parsing JSON '{}'", self.packagePid)
            finally:
                payload.close()
        except StorageException:
            self.log.error("Error accessing '{}'", self.packagePid)
            return

    def __savePackageData(self):
        jsonString = String(self.packageData.toString(True))
        inStream = ByteArrayInputStream(jsonString.getBytes("UTF-8"))
        try:
            self.object.updatePayload(self.packagePid, inStream)
        except StorageException, e:
            traceback.print_exc()
            self.log.error("Error updating package data payload: ", e)

    def collectWhitespacePdfs(self, pid):
        if pid.endswith(self.pdfSuffix):
            sanitized = StringUtils.deleteWhitespace(pid)
            if not StringUtils.equals(pid, sanitized):
                self.log.debug('found a pdf with whitespace: %s' % pid)
                self.pdfs[pid] = sanitized

    def createLinkedFile(self, paths_dict):
        for next_path, link in paths_dict.iteritems():
            original_path = os.path.join(self.object.getPath(), next_path)
            self.log.debug('linking: %s, to: %s' % (link, original_path))
            self.object.createLinkedPayload(link, original_path)