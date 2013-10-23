from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.api.storage import StorageException
from com.googlecode.fascinator.common import JsonObject, JsonSimple
from com.googlecode.fascinator.common.solr import SolrResult

from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.lang import Exception
from java.util import TreeMap, TreeSet

from org.apache.commons.lang import StringEscapeUtils, WordUtils
from org.json.simple import JSONArray
import preview
from java.io import File

class DetailData:
    def __init__(self):
        pass

    def __activate__(self, context):
        self.page = context["page"]
        self.metadata = context["metadata"]
        self.Services = context["Services"]
        self.formData = context["formData"]
        self.log = context["log"]
        storage = context["Services"].getStorage()
        storedObj = storage.getObject(context["metadata"].getFirst("storage_id"))
        request = context["request"]
        version = request.getParameter("version")
        versionTfPackage = request.getParameter("versionParked")
        if version is not None:
            self.item = JsonSimple(File(storedObj.getPath() + "/version_tfpackage_" + version))
            self.version = preview.formatDate(version, "yyyyMMddHHmmss", "yyyy-MM-dd HH:mm:ss") 
            self.versionStr = "This version was created on " + self.version  
        else:
            self.version = None
            self.versionStr = ""
            self.item = preview.loadPackage(storedObj)

    def hasWorkflow(self):
        self.__workflowStep = self.metadata.getList("workflow_step_label")
        if self.__workflowStep.isEmpty():
            return False
        return True

    def hasWorkflowAccess(self):
        userRoles = self.page.authentication.get_roles_list()
        workflowSecurity = self.metadata.getList("workflow_security")
        for userRole in userRoles:
            if userRole in workflowSecurity:
                return True
        return False

    def getWorkflowStep(self):
        return self.__workflowStep[0]

    def getFirst(self, field):
        return self.escapeHtml(self.metadata.getFirst(field))

    def getList(self, baseKey):
        if baseKey[-1:] != ".":
            baseKey = baseKey + "."
        valueMap = TreeMap()
        metadata = self.metadata.getJsonObject()
        for key in [k for k in metadata.keySet() if k.startswith(baseKey)]:
            value = metadata.get(key)
            ## adding test below since UI is moving away from SOLR data storage, please add to detail scripts to prevent a "missing" output. 
            if value:
                field = key[len(baseKey):]
                index = field[:field.find(".")]
                if index == "":
                    valueMapIndex = field[:key.rfind(".")]
                    dataIndex = "value"
                else:
                    valueMapIndex = index
                    dataIndex = field[field.find(".")+1:]
                #print "%s. '%s'='%s' ('%s','%s')" % (index, key, value, valueMapIndex, dataIndex)
                data = valueMap.get(valueMapIndex)
                #print "**** ", data
                if not data:
                    data = TreeMap()
                    valueMap.put(valueMapIndex, data)
                if len(value) == 1:
                    value = value.get(0)
                data.put(dataIndex, value)
        return valueMap

    def getSortedKeySet(self):
        return TreeSet(self.metadata.getJsonObject().keySet())

    def escapeHtml(self, value):
        if value:
            return StringEscapeUtils.escapeHtml(value) or ""
        return ""

    def getCurationData(self, oid):
        json = JsonObject()
        try:
            # Get the object from storage
            storage = self.Services.getStorage()
            object = storage.getObject(oid)

            # Find the package payload
            payload = None
            pidList = object.getPayloadIdList()
            for pid in pidList:
                if (pid.endswith(".tfpackage")):
                    payload = object.getPayload(pid)
            # Not found?
            if payload is None:
                self.log.error(" * detail.py => Can't find package data!")
                json.put("error", True)
                return json

            # Parse the data
            data = JsonSimple(payload.open())
            payload.close()

            # Some basic cosmetic fixes
            relations = data.writeArray("relationships")
            for relation in relations:
                if not relation.containsKey("field"):
                    relation.put("field", "From Object "+relation.get("oid"))

            # Return it
            json.put("error", False)
            json.put("relationships", relations)
            return json
        except StorageException, ex:
            self.log.error(" * detail.py => Storage Error accessing data: ", ex)
            json.put("error", True)
            return json
        except Exception, ex:
            self.log.error(" * detail.py => Error accessing data: ", ex)
            json.put("error", True)
            return json

    def getAttachedFiles(self, oid):
        # Build a query
        req = SearchRequest("attached_to:%s" % oid)
        req.setParam("rows", "1000")
        # Run a search
        out = ByteArrayOutputStream()
        self.Services.getIndexer().search(req, out)
        result = SolrResult(ByteArrayInputStream(out.toByteArray()))
        # Process results
        docs = JSONArray()
        for doc in result.getResults():
            attachmentType = self.escapeHtml(WordUtils.capitalizeFully(doc.getFirst("attachment_type").replace("-", " ")))
            accessRights = self.escapeHtml(WordUtils.capitalizeFully(doc.getFirst("access_rights")))
            entry = JsonObject()
            entry.put("filename",        self.escapeHtml(doc.getFirst("filename")))
            entry.put("attachment_type", attachmentType)
            entry.put("access_rights",   accessRights)
            entry.put("id",              self.escapeHtml(doc.getFirst("id")))
            docs.add(entry)
        return docs

    def getAnzsrcCode(self, code):
        uri = code.get("rdf:resource")
        return uri[uri.rfind("/")+1:]
