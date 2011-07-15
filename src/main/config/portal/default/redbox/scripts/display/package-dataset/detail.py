from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.common import JsonObject
from com.googlecode.fascinator.common.solr import SolrResult

from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.util import TreeMap, TreeSet

from org.apache.commons.lang import StringEscapeUtils, WordUtils
from org.json.simple import JSONArray

class DetailData:
    def __init__(self):
        pass

    def __activate__(self, context):
        self.page = context["page"]
        self.metadata = context["metadata"]
        self.Services = context["Services"]
        self.formData = context["formData"]

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

    def getAttachedFiles(self):
        # Build a query
        req = SearchRequest("attached_to:%s" % self.metadata.get("oid"))
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
