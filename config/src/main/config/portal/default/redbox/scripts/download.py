import os

from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.api.storage import StorageException
from com.googlecode.fascinator.common.solr import SolrDoc, SolrResult

from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.lang import Boolean
from java.net import URLDecoder

from org.apache.commons.io import IOUtils

class DownloadData:
    def __init__(self):
        pass

    def __activate__(self, context):
        self.services = context["Services"]
        self.contextPath = context["contextPath"]
        self.pageName = context["pageName"]
        self.portalId = context["portalId"]
        self.request = context["request"]
        self.response = context["response"]
        self.formData = context["formData"]
        self.page = context["page"]
        self.log = context["log"]

        self.__metadata = SolrDoc(None)
        object = None
        payload = None

        # URL basics
        basePath = self.portalId + "/" + self.pageName
        fullUri = URLDecoder.decode(self.request.getAttribute("RequestURI"))
        uri = fullUri[len(basePath)+1:]

        # Turn our URL into objects
        object, payload = self.__resolve(uri)
        if object is None:
            if uri.endswith("/"):
                self.log.error("Object 404: '{}'", uri)
                self.response.setStatus(404);
                writer = self.response.getPrintWriter("text/plain; charset=UTF-8")
                writer.println("Object not found")
                writer.close()
                return
            else:
                # Sometimes adding a slash to the end will resolve the problem
                self.log.error("Redirecting, object 404: '{}'", uri)
                self.response.sendRedirect(context["urlBase"] + fullUri + "/")
                return

        # Ensure solr metadata is useable
        oid = object.getId()
        if self.isIndexed():
            self.__metadata = self.__solrData.getResults().get(0)
        else:
            self.__metadata.getJsonObject().put("id", oid)
        #print "URI='%s' OID='%s' PID='%s'" % (uri, object.getId(), payload.getId())

        

        ## The byte range cache will check for byte range requests first
        self.cache = self.services.getByteRangeCache()
        processed = self.cache.processRequest(self.request, self.response, payload)
        if processed:
            # We don't need to return data, the cache took care of it.
            return

        # Now the 'real' work of payload retrieval
        if payload is not None:
            filename = os.path.split(payload.getId())[1]
            mimeType = payload.getContentType()
            if mimeType == "application/octet-stream":
                self.response.setHeader("Content-Disposition", "attachment; filename=%s" % filename)

            type = payload.getContentType()
            # Enocode textual responses before sending
            if type is not None and type.startswith("text/"):
                out = ByteArrayOutputStream()
                IOUtils.copy(payload.open(), out)
                payload.close()
                writer = self.response.getPrintWriter(type + "; charset=UTF-8")
                writer.println(out.toString("UTF-8"))
                writer.close()
            # Other data can just be streamed out
            else:
                if type is None:
                    # Send as raw data
                    out = self.response.getOutputStream("application/octet-stream")
                else:
                    out = self.response.getOutputStream(type)
                IOUtils.copy(payload.open(), out)
                payload.close()
                object.close()
                out.close()
        else:
            self.response.setStatus(404)
            writer = self.response.getPrintWriter("text/plain; charset=UTF-8")
            writer.println("Resource not found: uri='%s'" % uri)
            writer.close()

    def getAllowedRoles(self):
        metadata = self.getMetadata()
        if metadata is not None:
            return metadata.getList("security_filter")
        else:
            return []

    def getViewUsers(self):
        metadata = self.getMetadata()
        if metadata is not None:
            return metadata.getList("security_exception")
        else:
            return []
        
    def getMetadata(self):
        return self.__metadata      

    def isDetail(self):
        preview = Boolean.parseBoolean(self.formData.get("preview", "false"))
        return not (self.request.isXHR() or preview)

    def isIndexed(self):
        found = self.__solrData.getNumFound()
        return (found is not None) and (found == 1)

    def __resolve(self, uri):
        # Grab OID from the URL
        slash = uri.find("/")
        if slash == -1:
            return None, None
        oid = uri[:slash]

        # Query solr for this object
        self.__loadSolrData(oid)
        if not self.isIndexed():
            print "WARNING: Object '%s' not found in index" % oid
            sid = None
        else:
            # Query storage for this object
            sid = self.__solrData.getResults().get(0).getFirst("storage_id")

        try:
            if sid is None:
                # Use the URL OID
                object = self.services.getStorage().getObject(oid)
            else:
                # We have a special storage ID from the index
                object = self.services.getStorage().getObject(sid)
        except StorageException, e:
            #print "Failed to access object: %s" % (str(e))
            return None, None

        # Grab the payload from the rest of the URL
        pid = uri[slash+1:]
        if pid == "":
            # We want the source
            pid = object.getSourceId()

        # Now get the payload from storage
        try:
            payload = object.getPayload(pid)
        except StorageException, e:
            #print "Failed to access payload: %s" % (str(e))
            return None, None

        # We're done
        return object, payload

    def __loadSolrData(self, oid):
        portal = self.page.getPortal()
        query = 'id:"%s"' % oid
        if self.isDetail() and portal.getSearchQuery():
            query += " AND " + portal.getSearchQuery()
        req = SearchRequest(query)
        req.addParam("fq", 'item_type:"object"')
        if self.isDetail():
            req.addParam("fq", portal.getQuery())
            current_user = self.page.authentication.get_username()
            security_roles = self.page.authentication.get_roles_list()
            security_exceptions = 'security_exception:"' + current_user + '"'
            owner_query = 'owner:"' + current_user + '"'
            security_query = "(" + security_exceptions + ") OR (" + owner_query + ") OR ("+ security_exceptions +")"    
            req.addParam("fq", security_query)
        out = ByteArrayOutputStream()
        self.log.error("searching to get solrData")
        self.services.getIndexer().search(req, out)
        self.__solrData = SolrResult(ByteArrayInputStream(out.toByteArray()))
