import md5, os, time

from au.edu.usq.fascinator.api.storage import StorageException
from au.edu.usq.fascinator.indexer.rules import AddField, New

#
# Available objects:
#    indexer    : Indexer instance
#    log        : Logger instance
#    jsonConfig : JsonConfigHelper of our harvest config file
#    rules      : RuleManager instance
#    object     : DigitalObject to index
#    payload    : Payload to index
#    params     : Metadata Properties object
#    pyUtils    : Utility object for accessing app logic
#

def indexList (name, values):
    for value in values:
        rules.add(AddField(name, value))

def getNodeValues (doc, xPath):
    nodes = doc.selectNodes(xPath)
    valueList = []
    if nodes:
        for node in nodes:
            #remove duplicates:
            nodeValue = node.getText()
            if nodeValue not in valueList:
                valueList.append(node.getText())
    return valueList

def mapVuFind (ourField, theirField, map):
    for value in map.getList(theirField):
        rules.add(AddField(ourField, value))

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
rules.add(AddField("item_type", itemType))
rules.add(AddField("last_modified", time.strftime("%Y-%m-%dT%H:%M:%SZ")))
rules.add(AddField("harvest_config", params.getProperty("jsonConfigOid")))
rules.add(AddField("harvest_rules",  params.getProperty("rulesOid")))

# Security
roles = pyUtils.getRolesWithAccess(oid)
if roles is not None:
    for role in roles:
        rules.add(AddField("security_filter", role))
else:
    # Default to guest access if Null object returned
    schema = pyUtils.getAccessSchema("derby");
    schema.setRecordId(oid)
    schema.set("role", "guest")
    pyUtils.setAccessSchema(schema, "derby")
    rules.add(AddField("security_filter", "guest"))

if params.getProperty("recordType") == "marc-author":
    rules.add(AddField("storage_id", oid))
    title = params["title"]
    author = params["author"]
    rules.add(AddField("dc_title", author))
    rules.add(AddField("dc_description", "Author name extracted from MARCXML"))
    rules.add(AddField("application/x-fascinator-author"))
    rules.add(AddField("recordtype", "author"))
    rules.add(AddField("repository_name", params["repository.name"]))
    rules.add(AddField("repository_type", params["repository.type"]))
elif pid == metaPid:
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

    ### Index the marc metadata extracted from solrmarc
    try:
        marcPayload = object.getPayload("metadata.json")
        marc = pyUtils.getJsonObject(marcPayload.open())
        marcPayload.close()
        if marc is not None:
            coreFields = {
                "id" : "storage_id",
                "recordtype" : "recordtype",
                "title" : "dc_title",
                "author_100" : "dc_creator",
                "author_700" : "dc_creator",
                "university" : "university",
                "faculty" : "faculty",
                "school" : "school"
            }

            for k,v in coreFields.iteritems():
                mapVuFind(v, k, marc)

            rules.add(AddField("display_type", "marcxml"))

    except StorageException, e:
        print "Could not find marc data (%s)" % str(e)

# On the first index after a harvest we need to put the transformer back into
#  the picture for reharvest actions to work.
renderer = params.getProperty("renderQueue")
if renderer is not None and renderer == "":
    params.setProperty("renderQueue", "solrmarc");
    params.setProperty("objectRequiresClose", "true");
