from java.io import ByteArrayInputStream
from java.lang import String
from java.io import StringWriter
from org.apache.commons.io import IOUtils

import sys
pathToWorkflows = "../../home/harvest/workflows/"
if sys.path.count(pathToWorkflows)==0:
    sys.path.append(pathToWorkflows)

import time
from json2 import read as jsonReader, write as jsonWriter



from au.edu.usq.fascinator.api.storage import StorageException
from au.edu.usq.fascinator.common import JsonConfigHelper
from au.edu.usq.fascinator.common.storage import StorageUtils
from au.edu.usq.fascinator.indexer.rules import AddField, New
#
# Available objects:
#    indexer    : Indexer instance
#    jsonConfig : JsonConfigHelper of our harvest config file
#    rules      : RuleManager instance
#    object     : DigitalObject to index
#    payload    : Payload to index
#    params     : Metadata Properties object
#    pyUtils    : Utility object for accessing app logic
#

def indexList(name, values):
    for value in values:
        rules.add(AddField(name, value))

def grantAccess(object, newRole):
    schema = object.getAccessSchema("derby");
    schema.setRecordId(oid)
    schema.set("role", newRole)
    object.setAccessSchema(schema, "derby")

def revokeAccess(object, oldRole):
    schema = object.getAccessSchema("derby");
    schema.setRecordId(oid)
    schema.set("role", oldRole)
    object.removeAccessSchema(schema, "derby")


def getPackage():
    sourceId = object.getSourceId()
    payload = object.getPayload(sourceId)
    writer = StringWriter()
    IOUtils.copy(payload.open(), writer)
    tfpackage = jsonReader(writer.toString())
    payload.close()
    return tfpackage

def getWorkflowMetadata():
    wfPayload = object.getPayload("workflow.metadata")
    wfMeta = JsonConfigHelper(wfPayload.open())
    wfPayload.close()
    return wfMeta

def setWorkflowMetadata(metadata):
    try:
        jsonString = String(metadata.toString())
        inStream = ByteArrayInputStream(jsonString.getBytes("UTF-8"))
        self.object.updatePayload("workflow.metadata", inStream)
        return True
    except StorageException, e:
        return False

#start with blank solr document
rules.add(New())

#common fields
oid = object.getId()
pid = payload.getId()
metaPid = params.getProperty("metaPid", "DC")
if pid == metaPid:
    itemType = "object"
else:
    oid += "/" + pid
    itemType = "datastream"
    rules.add(AddField("identifier", pid))

rules.add(AddField("id", oid))
rules.add(AddField("storage_id", oid))
rules.add(AddField("item_type", itemType))
rules.add(AddField("last_modified", time.strftime("%Y-%m-%dT%H:%M:%SZ")))

item_security = []

if pid == metaPid:
    print "*************** dataset-rules.py ***************** 3"
    for payloadId in object.getPayloadIdList():
        try:
            payload = object.getPayload(payloadId)
            if str(payload.getType())=="Thumbnail":
                rules.add(AddField("thumbnail", payload.getId()))
            elif str(payload.getType())=="Preview":
                rules.add(AddField("preview", payload.getId()))
            elif str(payload.getType())=="AltPreview":
                rules.add(AddField("altpreview", payload.getId()))
        except Exception, e:
            pass
    #only need to index metadata for the main object
    rules.add(AddField("repository_name", params["repository.name"]))
    rules.add(AddField("repository_type", params["repository.type"]))

    ##
    # Workflow data
    WORKFLOW_ID = "dataset"
    wfChanged = False
    message_list = None
    workflow_security = []
    try:
        wfMeta = getWorkflowMetadata()
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
        stages = jsonConfig.getJsonList("stages")
        for stage in stages:
            if stage.get("name") == targetStep:
                wfMeta.set("label", stage.get("label"))
                item_security = stage.getList("visibility")
                workflow_security = stage.getList("security")
                if wfChanged == True:
                    message_list = stage.getList("message")
    except StorageException, e:
        # No workflow payload, time to create
        wfChanged = True
        wfMeta = JsonConfigHelper()
        wfMeta.set("id", WORKFLOW_ID)
        wfMeta.set("step", "pending")
        wfMeta.set("pageTitle", "Dataset Metadata.")
        stages = jsonConfig.getJsonList("stages")
        for stage in stages:
            if stage.get("name") == "pending":
                wfMeta.set("label", stage.get("label"))
                item_security = stage.getList("visibility")
                workflow_security = stage.getList("security")
                message_list = stage.getList("message")
    # Has the workflow metadata changed?
    if wfChanged == True:
        jsonString = String(wfMeta.toString())
        inStream = ByteArrayInputStream(jsonString.getBytes("UTF-8"))
        try:
            StorageUtils.createOrUpdatePayload(object, "workflow.metadata", inStream)
        except StorageException, e:
            print " * dataset-rules.py : Error updating workflow payload"

    rules.add(AddField("workflow_id", wfMeta.get("id")))
    rules.add(AddField("workflow_step", wfMeta.get("step")))
    rules.add(AddField("workflow_step_label", wfMeta.get("label")))
    for group in workflow_security:
        rules.add(AddField("workflow_security", group))
    ##

    # Index our metadata finally
    titleList = ["New dataset package"]
    descriptionList = []
    formatList = ["application/x-fascinator-package"]

    customFields = {}
    try:
        # Form processing
        formData = wfMeta.getJsonList("formData")
        print "formData='%s'" % str(formData)
        if formData.size() > 0:
            formData = formData[0]
        else:
            formData = None
        coreFields = ["title", "description"]
        if formData is not None:
            # Core fields
            title = formData.getList("title")
            if title:
                titleList = title
            description = formData.getList("description")
            if description:
                descriptionList = description
            # Non-core fields
            data = formData.getMap("/")
            for field in data.keySet():
                if field not in coreFields:
                    customFields[field] = formData.getList(field)
    except Exception, e:
        print "Error processing form data - '%s'" % str(e)

    tfpackage = getPackage()
    titleList = [tfpackage.get("title", "[Untitled dataset package]")]
    descriptionList = [tfpackage.get("description", "")]
    print "titleList='%s'" % titleList
    print "descriptionList='%s'" % descriptionList

    # Index our metadata finally    
    indexList("dc_title", titleList)
    indexList("dc_description", descriptionList)

    for key in customFields:
        indexList(key, customFields[key])

    rules.add(AddField("displayType", "package-dataset"))
    rules.add(AddField("display_type", "package-dataset"))

    # AFTER saving the data, send messages for workflows
    # Any messages for the new step?
    if message_list is not None and len(message_list) > 0:
        msg = JsonConfigHelper()
        msg.set("oid", oid)
        message = msg.toString()
        for target in message_list:
            pyUtils.sendMessage(target, message)

# Security
roles = pyUtils.getRolesWithAccess(oid)
if roles is not None:
    # For every role currently with access
    for role in roles:
        # Should show up, but during debugging we got a few
        if role != "":
            if role in item_security:
                # They still have access
                rules.add(AddField("security_filter", role))
            else:
                # Their access has been revoked
                revokeAccess(pyUtils, role)
    # Now for every role that the new step allows access
    for role in item_security:
        if role not in roles:
            # Grant access if new
            grantAccess(pyUtils, role)
            rules.add(AddField("security_filter", role))
# No existing security
else:
    if item_security is None:
        # Guest access if none provided so far
        grantAccess(pyUtils, "guest")
        rules.add(AddField("security_filter", role))
    else:
        # Otherwise use workflow security
        for role in item_security:
            # Grant access if new
            grantAccess(pyUtils, role)
            rules.add(AddField("security_filter", role))
# Ownership
owner = params.getProperty("owner", "system")
if owner is None:
    rules.add(AddField("owner", "system"))
else:
    rules.add(AddField("owner", owner))

# add owner to workflow security
AddField("workflow_security", owner)