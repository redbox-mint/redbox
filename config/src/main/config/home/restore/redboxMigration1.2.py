import re
import sys
import traceback

from com.googlecode.fascinator.api.storage import StorageException
from com.googlecode.fascinator.common import JsonSimple

from java.io import ByteArrayInputStream
from java.lang import Exception
from java.lang import String

class MigrateData:
    def __init__(self):
        self.workflowPid = "workflow.metadata"
        self.packagePidSuffix = ".tfpackage"
        self.redboxVersion = None

        self.listRegex = re.compile(r"""
            (?P<PREFIX>.+)       # Starts with anything
            \.(?P<LIST>\d+)      # Lists have integers eg. '.1.'
            (\.(?P<SUFFIX>.+))*  # Some lists have subfields
        """, re.VERBOSE)

        self.errorTemplate = """Error occured in Jython script:
====
 * LINE #:{}
 * TYPE: {}
 * VALUE: {}
 * LINE STACK TRACE:
{}
===="""

    def __activate__(self, bindings):
        # Prepare variables
        self.systemConfig = bindings["systemConfig"]
        self.object       = bindings["object"]
        self.log          = bindings["log"]
        self.audit        = bindings["auditMessages"]
        self.pidList      = None

        # Look at some data
        self.oid = self.object.getId()
        if self.redboxVersion is None:
            self.redboxVersion = self.systemConfig.getString(None, ["redbox.version.string"])
        if self.redboxVersion is None:
            self.log.error("Error, could not determine system version!")
            return

        # Process the form
        try:
            self.__formData()
        except:
            self.__logError()

    def __logError(self):
        exc_type, exc_value, exc_tb = sys.exc_info()
        stack_list = traceback.extract_tb(exc_tb)
        stack_string = ""
        lineNum = 0
        gap = "   "
        for stack_line in stack_list:
            scriptName, lineNum, method, source = stack_line
            stack_string += "%s-  %s() #%s\n" % (gap, method, lineNum)
            gap += "  "
        self.log.error(self.errorTemplate, [lineNum,
                exc_type, exc_value, stack_string])

    def __formData(self):
        # Find our workflow form data
        packagePid = None
        try:
            self.pidList = self.object.getPayloadIdList()
            for pid in self.pidList:
                if pid.endswith(self.packagePidSuffix):
                    packagePid = pid
        except StorageException:
            self.log.error("Error accessing object PID list for object '{}' ", self.oid)
            return
        if packagePid is None:
            self.log.debug("Object '{}' has no form data", self.oid)
            return

        # Retrieve our form data
        workflowData = None
        try:
            payload = self.object.getPayload(packagePid)
            try:
                workflowData = JsonSimple(payload.open())
            except Exception:
                self.log.error("Error parsing JSON '{}'", packagePid)
            finally:
                payload.close()
        except StorageException:
            self.log.error("Error accessing '{}'", packagePid)
            return

        # Test our version data
        version = workflowData.getString("{NO VERSION}", ["redbox:formVersion"])
        oldData = String(workflowData.toString(True))
        if version != self.redboxVersion:
            self.log.info("OID '{}' requires an upgrade: '{}' => '{}'", [self.oid, version, self.redboxVersion])
            # The version data is old, run our upgrade
            #   function to see if any alterations are
            #   required. Most likely at least the
            #   version number will change.
            newWorkflowData = self.__upgrade(version, workflowData)
        else:
            newWorkflowData = self.__hotfix(workflowData)
            if newWorkflowData is not None:
                self.log.debug("OID '{}' was hotfixed for v1.2 'dc:type' bug", self.oid)
            else:
                self.log.debug("OID '{}' requires no work, skipping", self.oid)
                return

        # Backup our data first
        backedUp = self.__backup(oldData)
        if not backedUp:
            self.log.error("Upgrade aborted, data backup failed!")
            return

        # Save the newly modified data
        jsonString = String(newWorkflowData.toString(True))
        inStream = ByteArrayInputStream(jsonString.getBytes("UTF-8"))
        try:
            self.object.updatePayload(packagePid, inStream)
        except StorageException, e:
            self.log.error("Error updating workflow payload: ", e)

    def __hotfix(self, formData):
        oldType = formData.getString(None, ["dc:type"])
        newType = formData.getString(None, ["dc:type.rdf:PlainLiteral"])
        if oldType != newType or newType is None:
            self.log.debug("Bugged Type?: v1.4: '{}', OLD: '{}'", newType, oldType)
        else:
            ## No fix required
            return None

        ## Get Backup data
        ## NOTE: The only known production system affected by this bug
        ## was caught during a v1.4 upgrade. Alter this line if required.
        pid = "1.4.workflow.backup"
        oldData = None
        try:
            payload = self.object.getPayload(pid)
            try:
                oldData = JsonSimple(payload.open())
            except Exception:
                self.log.error("Error parsing JSON '{}'", pid)
            finally:
                payload.close()
        except StorageException:
            self.log.error("Error accessing '{}'", pid)
            return None

        oldType = oldData.getString(None, ["dc:type"])
        self.log.debug("Old Type: '{}' => 'dc:type.rdf:PlainLiteral'", oldType)
        formData.getJsonObject().put("dc:type.rdf:PlainLiteral", oldType);
        return formData

    def __upgrade(self, version, formData):
        # These fields are handled specially
        ignoredFields = ["metaList", "redbox:formVersion", "redbox:newForm"]

        # Prepare a new JSON setup for upgraded data
        newJsonSimple = JsonSimple()
        newJsonObject = newJsonSimple.getJsonObject()
        metaList = newJsonSimple.writeArray(["metaList"])

        oldJsonObject = formData.getJsonObject()
        for key in oldJsonObject.keySet():
            oldField = str(key)
            if oldField not in ignoredFields:
                newField = self.__parseFieldName(oldField)
                metaList.add(newField)
                newJsonObject.put(newField, oldJsonObject.get(key))

        # Form management
        newJsonObject.put("redbox:formVersion", self.redboxVersion)
        newForm = oldJsonObject.get("redbox:newForm")
        if newForm is not None:
            newJsonObject.put("redbox:newForm", newForm)

        #########
        # Some final custom modifications more complicated than most fields
        #########

        # Old URL checkbox 'on' equals new ID Origin 'internal'
        urlOrigin = oldJsonObject.get("url_useRecordId")
        if urlOrigin is not None and urlOrigin == "on":
            newJsonObject.put("dc:identifier.redbox:origin", "internal")

        # Related data should default to being unlinked if from legacy forms
        counter = 1
        template = "dc:relation.vivo:Dataset"
        newIdField = "%s.%s.dc:identifier" % (template, counter)
        while newJsonObject.containsKey(newIdField):
            newOriginField = "%s.%s.redbox:origin" % (template, counter)
            newJsonObject.put(newOriginField, "external")
            newPublishField = "%s.%s.redbox:publish" % (template, counter)
            newJsonObject.put(newPublishField, "off")
            counter += 1
            newIdField = "%s.%s.dc:identifier" % (template, counter)

        self.audit.add("Migration tool. Version upgrade performed '%s' => '%s'" % (version, self.redboxVersion))
        return newJsonSimple

    def __parseFieldName(self, field):
        baseField = field
        digits = None

        match = self.listRegex.match(field)
        # Look for lists
        if match is not None:
            prefix = match.group('PREFIX')
            digits = match.group('LIST')
            # How does it end?
            suffix = match.group('SUFFIX')
            if suffix is None:
                baseField = "%s.0" % prefix
            else:
                baseField = "%s.0.%s" % (prefix, suffix)

        # Map the base fields to their new format, digits will
        #  be put into the new base fields for us.
        return self.__mapField(baseField, digits)

    def __backup(self, oldData):
        # Find an available PID to backup to
        counter = 1
        prefix = "%s.workflow.backup" % self.redboxVersion
        backupPid = prefix
        while self.pidList.contains(backupPid):
            counter += 1
            backupPid = "%s.%s" % (prefix, counter)

        # Store the data in this PID
        inStream = ByteArrayInputStream(oldData.getBytes("UTF-8"))
        try:
            self.object.createStoredPayload(backupPid, inStream)
            self.audit.add("Migration tool. Data backed up: '%s'" % (backupPid))
            return True
        except StorageException, e:
            self.log.error("Error backing up workflow payload: ", e)
            return False

    ## Version 1.2 Field mappings from v1.1
    def __mapField(self, oldBase, digits):
        newField = None

        # GENERAL tab
        if oldBase == "dc:language":
            newField = "dc:language.dc:identifier"
        if oldBase == "dc:type":
            newField = "dc:type.rdf:PlainLiteral"

        # COVERAGE tab
        elif oldBase == "dc:coverage.from":
            newField = "dc:coverage.vivo:DateTimeInterval.vivo:start"
        elif oldBase == "dc:coverage.to":
            newField = "dc:coverage.vivo:DateTimeInterval.vivo:end"
        elif oldBase == "time_period":
            newField = "dc:coverage.redbox:timePeriod"

        elif oldBase == "location.0.type":
            newField = "dc:coverage.vivo:GeographicLocation.0.dc:type"
        elif oldBase == "location.0.dcmi:name":
            newField = "dc:coverage.vivo:GeographicLocation.0.gn:name"
        elif oldBase == "location.0.dcmi:east":
            newField = "dc:coverage.vivo:GeographicLocation.0.geo:long"
        elif oldBase == "location.0.dcmi:north":
            newField = "dc:coverage.vivo:GeographicLocation.0.geo:lat"
        elif oldBase == "location.0.geonames:uri":
            newField = "dc:coverage.vivo:GeographicLocation.0.dc:identifier"

        # DESCRIPTION tab
        elif oldBase == "citations.0":
            newField = "dc:relation.swrc:Publication.0.dc:identifier"
        elif oldBase == "citations.0.title":
            newField = "dc:relation.swrc:Publication.0.dc:title"
        elif oldBase == "citations.0.notes":
            newField = "dc:relation.swrc:Publication.0.skos:note"

        elif oldBase == "website.0":
            newField = "dc:relation.bibo:Website.0.dc:identifier"
        elif oldBase == "website.0.title":
            newField = "dc:relation.bibo:Website.0.dc:title"
        elif oldBase == "website.0.notes":
            newField = "dc:relation.bibo:Website.0.skos:note"

        elif oldBase == "data.0":
            newField = "dc:relation.vivo:Dataset.0.dc:identifier"
        elif oldBase == "data.0.title":
            newField = "dc:relation.vivo:Dataset.0.dc:title"
        elif oldBase == "data.0.notes":
            newField = "dc:relation.vivo:Dataset.0.skos:note"

        # PEOPLE tab
        elif oldBase == "dc:creator.foaf:Person.0.dc:title":
            newField = "dc:creator.foaf:Person.0.foaf:name"
        elif oldBase == "dc:creator.foaf:Person.0.ci":
            newField = "dc:creator.foaf:Person.0.redbox:isCoPrimaryInvestigator"
        elif oldBase == "dc:creator.foaf:Person.0.pi":
            newField = "dc:creator.foaf:Person.0.redbox:isPrimaryInvestigator"
        elif oldBase == "dc:creator.foaf:Person.0.association":
            newField = "dc:creator.foaf:Person.0.foaf:Organization.dc:identifier"
        elif oldBase == "dc:creator.foaf:Person.0.association.skos:prefLabel":
            newField = "dc:creator.foaf:Person.0.foaf:Organization.skos:prefLabel"

        elif oldBase == "primaryContact.dc:identifier":
            newField = "locrel:prc.foaf:Person.dc:identifier"
        elif oldBase == "primaryContact.dc:title":
            newField = "locrel:prc.foaf:Person.foaf:name"
        elif oldBase == "primaryContact.foaf:givenName":
            newField = "locrel:prc.foaf:Person.foaf:givenName"
        elif oldBase == "primaryContact.foaf:familyName":
            newField = "locrel:prc.foaf:Person.foaf:familyName"
        elif oldBase == "primaryContact.foaf:email":
            newField = "locrel:prc.foaf:Person.foaf:email"

        elif oldBase == "supervisor.0.dc:identifier":
            newField = "swrc:supervisor.foaf:Person.0.dc:identifier"
        elif oldBase == "supervisor.0.dc:title":
            newField = "swrc:supervisor.foaf:Person.0.foaf:name"
        elif oldBase == "supervisor.0.foaf:givenName":
            newField = "swrc:supervisor.foaf:Person.0.foaf:givenName"
        elif oldBase == "supervisor.0.foaf:familyName":
            newField = "swrc:supervisor.foaf:Person.0.foaf:familyName"

        elif oldBase == "collaborators.0":
            newField = "dc:contributor.locrel:clb.0.foaf:Agent"

        # SUBJECT tab
        elif oldBase == "dc:subject.keywords.0":
            newField = "dc:subject.vivo:keyword.0.rdf:PlainLiteral"

        elif oldBase == "research_activity":
            newField = "dc:subject.anzsrc:toa.rdf:resource"
        elif oldBase == "research_activity.skos:prefLabel":
            newField = "dc:subject.anzsrc:toa.skos:prefLabel"

        # RIGHTS tab
        elif oldBase == "access_conditions":
            newField = "dc:accessRights.rdf:PlainLiteral"
        elif oldBase == "restrictions":
            newField = "dc:accessRights.dc:RightsStatement"

        elif oldBase == "license_cc":
            newField = "redbox:creativeCommonsLicense.dc:identifier"
        elif oldBase == "license_cc.skos:prefLabel":
            newField = "redbox:creativeCommonsLicense.skos:prefLabel"
        elif oldBase == "license_other_name":
            newField = "dc:license.skos:prefLabel"
        elif oldBase == "license_other_url":
            newField = "dc:license.dc:identifier"

        # MANAGEMENT tab
        elif oldBase == "url":
            newField = "dc:identifier.rdf:PlainLiteral"
        elif oldBase == "url.0":
            newField = "bibo:Website.0.dc:identifier"
        elif oldBase == "physical_storage":
            newField = "vivo:Location.vivo:GeographicLocation.gn:name"
        elif oldBase == "location_notes":
            newField = "vivo:Location.vivo:GeographicLocation.skos:note"

        elif oldBase == "retention_period":
            newField = "redbox:retentionPeriod"
        elif oldBase == "extent":
            newField = "dc:extent"
        elif oldBase == "disposal_date":
            newField = "redbox:disposalDate"

        elif oldBase == "data_owner.0":
            newField = "locrel:own.foaf:Agent.0.foaf:name"
        elif oldBase == "data_custodian":
            newField = "locrel:dtm.foaf:Agent.foaf:name"
        elif oldBase == "affiliation":
            newField = "foaf:Organization.dc:identifier"
        elif oldBase == "affiliation.skos:prefLabel":
            newField = "foaf:Organization.skos:prefLabel"

        elif oldBase == "funding.0.rdf:resource":
            newField = "foaf:fundedBy.foaf:Agent.0.dc:identifier"
        elif oldBase == "funding.0.skos:prefLabel":
            newField = "foaf:fundedBy.foaf:Agent.0.skos:prefLabel"

        elif oldBase == "grant.0.uon:internal":
            newField = "foaf:fundedBy.vivo:Grant.0.redbox:internalGrant"
        elif oldBase == "grant.0.grantNumber":
            newField = "foaf:fundedBy.vivo:Grant.0.redbox:grantNumber"
        elif oldBase == "grant.0.dc:identifier":
            newField = "foaf:fundedBy.vivo:Grant.0.dc:identifier"
        elif oldBase == "grant.0.skos:prefLabel":
            newField = "foaf:fundedBy.vivo:Grant.0.skos:prefLabel"

        elif oldBase == "project_title":
            newField = "swrc:ResearchProject.dc:title"
        elif oldBase == "depositor":
            newField = "locrel:dpt.foaf:Person.foaf:name"
        elif oldBase == "data_size":
            newField = "dc:SizeOrDuration"
        elif oldBase == "policy":
            newField = "dc:Policy"
        elif oldBase == "management_plan":
            newField = "redbox:ManagementPlan.redbox:hasPlan"
        elif oldBase == "management_plan_notes":
            newField = "redbox:ManagementPlan.skos:note"

        # NOTES tab
        elif oldBase == "notes.0.date":
            newField = "skos:note.0.dc:created"
        elif oldBase == "notes.0.username":
            newField = "skos:note.0.foaf:name"
        elif oldBase == "notes.0.description":
            newField = "skos:note.0.dc:description"

        # SUBMISSION tab
        elif oldBase == "submitted":
            newField = "redbox:submissionProcess.redbox:submitted"
        elif oldBase == "submitDate":
            newField = "redbox:submissionProcess.dc:date"
        elif oldBase == "submitDescription":
            newField = "redbox:submissionProcess.dc:description"
        elif oldBase == "contactName":
            newField = "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:name"
        elif oldBase == "phoneNumber":
            newField = "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:phone"
        elif oldBase == "emailAddress":
            newField = "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:mbox"
        elif oldBase == "submitTitle":
            newField = "redbox:submissionProcess.dc:title"
        elif oldBase == "submitNotes":
            newField = "redbox:submissionProcess.skos:note"

        # An unchanged field (or custom)
        else:
            newField = oldBase

        # Important to note that v1.2 does not have any
        # fields that end in digits, so no ".0", only ".0."
        if digits is not None:
            newField = newField.replace(".0.", ".%s." % digits, 1);

        return newField