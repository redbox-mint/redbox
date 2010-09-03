from __main__ import Services, formData

from au.edu.usq.fascinator.common import JsonConfigHelper

from org.apache.commons.lang import StringEscapeUtils
from java.lang import Exception as JavaException, Boolean, String
from java.util import ArrayList, HashMap
from java.io import (InputStreamReader, ByteArrayInputStream,
    ByteArrayOutputStream, File, StringWriter)
from org.apache.commons.io import IOUtils
from au.edu.usq.fascinator.api.indexer import SearchRequest

from json2 import read as jsonReader, write as jsonWriter
import re


class DatasetWorkflowData(object):
    def __init__(self):
        pass

    def __activate__(self, context):
        print "**** datasetWorkflow.py"
        self.velocityContext = context
        formData = self.vc("formData")
        self.formData = formData

        self.__oid = formData.get("oid")
        self.__tfpackage = None
        self.__manifest = None
        self.__object = None
        func = formData.get("func", "")
        id = formData.get("id")
        result = None


        print "formData: %s" % formData
        try:
            if self.__oid:
                # get the package manifest
                self.__object = Services.getStorage().getObject(self.__oid)
                sourceId = self.__object.getSourceId()
                payload = self.__object.getPayload(sourceId)
                writer = StringWriter()
                IOUtils.copy(payload.open(), writer)
                self.__tfpackage = jsonReader(writer.toString())
                self.__manifest = self.__tfpackage.get("manifest")
                if not self.__manifest:
                    self.__manifest = {}
                    self.__tfpackage["manifest"]=self.__manifest
                payload.close()
                #print self.__oid
                #print self.__tfpackage
            if func=="getItem" and id:
                doc = self._getPackagedItem(id)
                result = jsonWriter({"doc":doc, "id":id})
            elif func=="addItem" and id and self.__tfpackage:
                title = formData.get("title")
                if self._addItem(id, title):
                    result = jsonWriter({"ok":"addedItem", "id":id})
                else:
                    result = jsonWriter({"id":id,
                        "error":"Failed to addItem id='%s', title='%s'" % (id, title)})
            elif func=="removeItem" and id and self.__tfpackage:
                if self._removeItem(id):
                    result = jsonWriter({"ok":"removedItem", "id":id})
                else:
                    result = jsonWriter({"id":id,
                        "error":"Failed to remove item"})
            elif func=="search":
                query = formData.get("query", "")
                pageNum = int(formData.get("pageNum", "1"))
                result = self.getSearchResults(query, pageNum)
        except Exception, e:
            log.error("Failed to load manifest", e);
            result = jsonWriter({"status":"error", "message":"%s" % str(e)})
        if self.__object:
            self.__object.close()
            self.__object=None
        if result is not None:
            writer = response.getPrintWriter("text/plain; charset=UTF-8")
            #writer = response.getPrintWriter("application/json; charset=UTF-8")
            writer.println(result)
            writer.close()
    
    # Get from velocity context
    def vc(self, index):
        if self.velocityContext[index] is not None:
            return self.velocityContext[index]
        else:
            log.error("ERROR: Requested context entry '" + index + "' doesn't exist")
            return None

    def getJsonMetadata(self):              # used
        return jsonWriter(self.__tfpackage)

    def getAjaxRequestUrl(self):
        return "../workflows/test.ajax"

    def getJsonTest(self):                  # used (testing)
        return jsonWriter("""Testing a string with ' and " and \n\rnewlines""")

    def getJsonPackagedItems(self):
        return jsonWriter(self._getPackagedItems())

    def getSearchResults(self, query=None, pageNum=1):
#        ##
#        import search
#        # setup the context
#        for name in bindings.keySet():
#            search.__dict__[name] = bindings.get(name)
#        #sData = search.SearchData()
#        ##
        from au.edu.usq.fascinator.api.indexer import SearchRequest
        portal = Services.portalManager.get(portalId)
        recordsPerPage = portal.recordsPerPage
        if query is None:
            query = ""
        query = query.strip()
        if query=="":
            query = "*:*"
        query += " AND NOT dc_format:'application/x-fascinator-package'"
        req = SearchRequest(query)
        req.setParam("facet", "true")
        req.setParam("rows", str(recordsPerPage))
        req.setParam("facet.field", portal.facetFieldList)
        req.setParam("facet.sort", str(portal.getFacetSort()))
        req.setParam("facet.limit", str(portal.facetCount))
        req.setParam("sort", "f_dc_title asc")
        req.addParam("fq", 'item_type:"object"')
        req.setParam("start", str((pageNum - 1) * recordsPerPage))
        #print "req='%s'" % req.toString()
        out = ByteArrayOutputStream()
        Services.indexer.search(req, out)
        writer = StringWriter()
        IOUtils.copy(ByteArrayInputStream(out.toByteArray()), writer)
        jsonStr = writer.toString()
        json = jsonReader(jsonStr)
        return jsonStr

        #page.authentication.is_admin()
        class Obj(object):pass
        page=Obj()
        page.authentication=Obj()
        def isAdmin():
            return True
        page.authentication.is_admin = isAdmin
        search.__dict__["page"] = page
        sData = search.SearchData()

        r = sData.getResult()
        return r

    def _addItem(self, id, title):
        # "node-eeceaa96721e8f5682b5bde81d0a6536" : {
        #      "id" : "eeceaa96721e8f5682b5bde81d0a6536",
        #      "title" : "icons.gif"    }
        try:
            nodeId = "node-%s" % id
            if self.__manifest.has_key(nodeId):
                print "Info. The manifest already contains nodeId '%s'" % nodeId
                return True
            self.__manifest[nodeId] = {"id":id, "title":title}
            self._savePackage()
            return True
        except Exception, e:
            print "Error adding an item to the manifest - '%s'" % str(e)
            return False

    def _removeItem(self, id):
        #print "_removeItem id='%s'" % id
        nodeId = "node-%s" % id
        item = self.__manifest.pop(nodeId)
        if item:
            self._savePackage()
            return True
        else:
            return False

    def _getPackagedItems(self):
        ids = []
        docs = []
        try:
            manifest = self.__tfpackage.get("manifest", {})     #### []
            for v in manifest.itervalues():
                id = v.get("id")
                ids.append(id)
            docs = self._search(ids)
        except Exception, e:
            pass
        return docs

    def _getPackagedItem(self, id):
        ids = [id]
        doc = None
        docs = self._search(ids)
        if len(docs):
            doc = docs[0]
        return doc


    def _search(self, ids):
        # id = "0a815e0473f54d98a8a74c36345fcceb"
        docs = []
        if len(ids)==0:
            return docs
        try:
            query = " or ".join(["id:%s" % id for id in ids])
            print "_search query='%s'" % query
            req = SearchRequest(query)
            req.setParam("sort", "f_dc_title asc")
            req.setParam("sort", "dateCreated asc")
            out = ByteArrayOutputStream()
            Services.indexer.search(req, out)
            writer = StringWriter()
            IOUtils.copy(ByteArrayInputStream(out.toByteArray()), writer)
            json = jsonReader(writer.toString())
            #print "json='%s'" % json
            response = json.get("response")
            if response:
                docs = response.get("docs", [])
        except Exception, e:
            print "********* ERROR: %s" % str(e)
        docs = [{
                "title":d.get("dc_title", [""])[0],
                "description":d.get("dc_description", [""])[0],
                "thumbnail":d.get("thumbnail"),
                "id":d.get("storage_id")
                } for d in docs]
        return docs

    def getFormData(self, field):
        return StringEscapeUtils.escapeHtml(self.formData.get(field, ""))

    def _savePackage(self):
        json = jsonWriter(self.__tfpackage)
        self.__object.updatePayload(self.__object.getSourceId(),
                        ByteArrayInputStream(String(json).getBytes("UTF-8")))



