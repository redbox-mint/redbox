from java.io import ByteArrayInputStream
from java.lang import String
import time

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
rules.add(AddField("recordtype", "master"))

item_security = []
workflow_security = []

if pid == metaPid:
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

    # Index our metadata finally
    titleList = ["New package"]
    creatorList = []
    contributorList = []
    descriptionList = []
    formatList = ["application/x-fascinator-package"]
    creationDate = []

    # Workflow data
    WORKFLOW_ID = "packaging"
    wfChanged = False
    customFields = {}
    message_list = None
    try:
        wfPayload = object.getPayload("workflow.metadata")
        wfMeta = JsonConfigHelper(wfPayload.open())
        wfPayload.close()

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

        # Form processing
        formData = wfMeta.getJsonList("formData")
        if formData.size() > 0:
            formData = formData[0]
        else:
            formData = None
        coreFields = ["title", "creator", "contributor", "description", "format", "creationDate"]
        if formData is not None:
            # Core fields
            title = formData.getList("title")
            if title:
                titleList = title
            creator = formData.getList("creator")
            if creator:
                creatorList = creator
            contributor = formData.getList("contributor")
            if contributor:
                contributorList = contributor
            description = formData.getList("description")
            if description:
                descriptionList = description
            format = formData.getList("format")
            if format:
                formatList = format
            creation = formData.getList("creationDate")
            if creation:
                creationDate = creation
            # Non-core fields
            data = formData.getMap("/")
            for field in data.keySet():
                if field not in coreFields:
                    customFields[field] = formData.getList(field)

    except StorageException, e:
        # No workflow payload, time to create
        wfChanged = True
        wfMeta = JsonConfigHelper()
        wfMeta.set("id", WORKFLOW_ID)
        wfMeta.set("step", "pending")
        wfMeta.set("pageTitle", "Name Authority Record")
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
            print " * name-authority.py : Error updating workflow payload"

    rules.add(AddField("workflow_id", wfMeta.get("id")))
    rules.add(AddField("workflow_step", wfMeta.get("step")))
    rules.add(AddField("workflow_step_label", wfMeta.get("label")))
    for group in workflow_security:
        rules.add(AddField("workflow_security", group))

    # Index our metadata finally
    indexList("dc_title", titleList)
    indexList("dc_creator", creatorList)  #no dc_author in schema.xml, need to check
    indexList("dc_contributor", contributorList)
    indexList("dc_description", descriptionList)
    indexList("dc_format", formatList)
    indexList("dc_date", creationDate)

    for key in customFields:
        indexList(key, customFields[key])

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
rules.add(AddField("workflow_security", owner))
rules.add(AddField("display_type", "name-authority"))
