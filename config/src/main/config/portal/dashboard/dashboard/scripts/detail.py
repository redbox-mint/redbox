import os, re

from download import DownloadData
from userAgreement import AgreementData

from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.api.storage import StorageException
from com.googlecode.fascinator.common import JsonSimple
from com.googlecode.fascinator.common.solr import SolrDoc, SolrResult

from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.lang import Boolean
from java.net import URLDecoder, URLEncoder

class DetailData:
    def __init__(self):
        self.userAgreement = AgreementData()

    def __activate__(self, context):
        self.velocityContext = context
        self.services = context["Services"]
        self.request = context["request"]
        self.response = context["response"]
        self.formData = context["formData"]
        self.page = context["page"]
        self.fileAccess = None

        self.uaActivated = False
        useDownload = Boolean.parseBoolean(self.formData.get("download", "true"))
        self.__isPreview = Boolean.parseBoolean(self.formData.get("preview", "false"))
        self.__inPackage = Boolean.parseBoolean(self.formData.get("inPackage", "false"))
        self.__previewPid = None
        self.__hasPid = False

        uri = URLDecoder.decode(self.request.getAttribute("RequestURI"))
        matches = re.match("^(.*?)/(.*?)/(?:(.*?)/)?(.*)$", uri)
        if matches and matches.group(3):
            self.__oid = matches.group(3)
            pid = matches.group(4)

            self.__metadata = SolrDoc(None)
            self.__object = None
            self.__readMetadata()

            # If we have a PID
            if pid:
                self.__hasPid = True
                if useDownload:
                    # Download the payload to support relative links
                    download = DownloadData()
                    download.__activate__(context)
                else:
                    # Render the detail screen with the alternative preview
                    self.__previewPid = pid
            # Otherwise, render the detail screen
            else:
                self.__previewPid = self.getPreview()

            if self.__previewPid:
                self.__previewPid = URLEncoder.encode(self.__previewPid, "UTF-8")
        else:
            # require trailing slash for relative paths
            q = ""
            if self.__isPreview:
                q = "?preview=true"
            self.response.sendRedirect("%s%s/%s" % (context["urlBase"], uri, q))

    def getAllowedRoles(self):
        metadata = self.getMetadata()
        if metadata is not None:
            return metadata.getList("security_filter")
        else:
            return []

    def getAllPreviews(self):
        list = self.getAltPreviews()
        preview = self.getPreview()
        if not list.contains(preview):
            list.add(preview)
        return list

    def getAltPreviews(self):
        return self.__metadata.getList("altpreview")

    def getFileName(self):
        return self.getObject().getSourceId()

    def getFileNameSplit(self, index):
        return os.path.splitext(self.getFileName())[index]

    def getFriendlyName(self, name):
        if name.startswith("dc_"):
            name = name[3:]
        if name.startswith("meta_"):
            name = name[5:]
        return name.replace("_", " ").capitalize()

    def getMetadata(self):
        return self.__metadata

    def getObject(self):
        return self.__object

    def getOid(self):
        return self.__oid

    def getPreview(self):
        return self.__metadata.getFirst("preview")

    def getPreviewPid(self):
        return self.__previewPid

    def getProperty(self, field):
        return self.getObject().getMetadata().getProperty(field)

    def getUserAgreement(self):
        if not self.uaActivated:
            self.userAgreement.__activate__(self.velocityContext, self.getMetadata())
            self.uaActivated = True
        return self.userAgreement

    def hasLocalFile(self):
        if self.fileAccess is None:
            self.fileAccess = False
            config = self.velocityContext["systemConfig"]
            if config is not None:
                self.fileAccess = config.getBoolean(False, ["portal", "file-access", "enabled"])

        if self.fileAccess:
            # get original file.path from object properties
            filePath = self.getProperty("file.path")
            return filePath and os.path.exists(filePath)
        else:
            return False

    def hasPid(self):
        return self.__hasPid

    def inPackage(self):
        return self.__inPackage

    def isAccessDenied(self):
        # check if the current user is the record owner
        if self.getObject() is not None:    
            current_user = self.page.authentication.get_username()    
            owner = self.getProperty("owner")
            if current_user == owner: 
                return False
        # check using role-based security
        myRoles = self.page.authentication.get_roles_list()
        allowedRoles = self.getAllowedRoles()
        if myRoles is None or allowedRoles is None:
            return True
        for role in myRoles:
            if role in allowedRoles:
                return False
        return True

    def isDetail(self):
        return not (self.request.isXHR() or self.__isPreview)

    def isIndexed(self):
        found = self.__solrData.getNumFound()
        return (found is not None) and (found == 1)

    def isPending(self):
        meta = self.getObject().getMetadata()
        status = meta.get("render-pending")
        return Boolean.parseBoolean(status)

    def setStatus(self, status):
        self.response.setStatus(status)

    def __getObject(self):
        self.__loadSolrData()

        if not self.isIndexed():
            print "WARNING: Object '%s' not found in index" % self.__oid
            sid = None
        else:
            # Query storage for this object
            sid = self.__solrData.getResults().get(0).getFirst("storage_id")

        try:
            if sid is None:
                # Use the URL OID
                object = self.services.getStorage().getObject(self.__oid)
            else:
                # We have a special storage ID from the index
                object = self.services.getStorage().getObject(sid)
        except StorageException, e:
            #print "Failed to access object: %s" % (str(e))
            return None

        return object

    def __loadSolrData(self):
        portal = self.page.getPortal()
        query = 'id:"%s"' % self.__oid
        if self.isDetail() and portal.getSearchQuery():
            query += " AND " + portal.getSearchQuery()
        req = SearchRequest(query)
        req.addParam("fq", 'item_type:"object"')
        if self.isDetail():
            req.addParam("fq", portal.getQuery())
        out = ByteArrayOutputStream()
        self.services.getIndexer().search(req, out)
        self.__solrData = SolrResult(ByteArrayInputStream(out.toByteArray()))

    def __readMetadata(self):
        self.__loadSolrData()
        if self.isIndexed():
            self.__metadata = self.__solrData.getResults().get(0)
            if self.__object is None:
                # Try again, indexed records might have a special storage_id
                self.__object = self.__getObject()
        else:
            self.__metadata.getJsonObject().put("id", self.__oid)