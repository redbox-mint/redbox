from au.edu.usq.fascinator.api import PluginManager
from au.edu.usq.fascinator.api.indexer import SearchRequest
from au.edu.usq.fascinator.api.transformer import TransformerException
from au.edu.usq.fascinator.common import FascinatorHome
from au.edu.usq.fascinator.common import JsonConfigHelper
from au.edu.usq.fascinator.common import JsonSimpleConfig
from au.edu.usq.fascinator.common import MessagingServices

from java.io import ByteArrayInputStream
from java.io import ByteArrayOutputStream
from java.io import StringWriter
from java.lang import Exception
from java.lang import String

from org.apache.commons.io import IOUtils
from org.apache.commons.lang import StringEscapeUtils

from json2 import read as jsonReader, write as jsonWriter

class DatasetData(object):
    def __init__(self):
        self.messaging = MessagingServices.getInstance()

    def __activate__(self, context):
        print "**** dataset.py"
        self.velocityContext = context
        formData = self.vc("formData")
        response = self.vc("response")
        self.__formData = formData
        self.isAjax = bool(formData.get("ajax"))                     ##
        self.__tfpackage = None
        self.__manifest = None
        self.__object = None
        self.__oid = formData.get("_oid") or formData.get("oid")
        self.__currentStep = None
        self.__currentStepLabel = None
        self.Services = context.get("Services")
        self.page = context.get("page")
        func = formData.get("func", "")
        id = formData.get("id")
        result = None

        #print "formData: %s" % formData
        bindings = self.vc("bindings")
        request = self.vc("request")
        if self.vc("request").method=="GET" and func!="":
            #print " ****************  func was '%s'" % func
            func = ""
        if func=="" and request.getParameter("func"):
            func = request.getParameter("func")
        print "func='%s', oid='%s', id='%s'" % (func, self.__oid, id)
        #print "------------------------------------------"
        try:
            if func=="file-upload":
                print "*****************"
                print "  file-upload"
                print "*****************"
                result = jsonWriter({"ok":"file-upload", "oid":self.__oid})
            if self.__oid:
                # get the package manifest
                self.__tfpackage = self._getTFPackage()
                self.__manifest = self.__tfpackage.get("manifest")
                if not self.__manifest:
                    self.__manifest = {}
                    self.__tfpackage["manifest"]=self.__manifest
                if func=="update-package-meta":
                    result = self._updatePackageMetadata()
                    result = jsonWriter(result)
                elif func=="update-package-meta-deposit":
                    print " update-package-meta-deposit"
                    result = self._updatePackageMetadata(True)
                    result = jsonWriter(result)
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
            elif func=="setItemRepresentation":
                title = formData.get("title")
                representation = formData.get("representation")
                result = self._setItemRepresentation(id, title, representation)
                result = jsonWriter(result)
            elif func=="getPackagedItems":
                docs = self._getPackagedItemsData()
                start = 0
                num = len(docs)
                #start = int(formData.get("start", "0"))
                #num = int(formData.get("num", str(len(docs))))
                result = jsonWriter(docs[start:num])
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

    def userRoles(self):
        return self.vc("page").authentication.get_roles_list()

    def username(self):
        # .is_admin(), .is_logged_in()
        return self.vc("page").authentication.get_username()

    def getCurrentStep(self):
        if self.__currentStep is None:
            wfMeta = self._getWorkflowMetadata()
            self.__currentStep = wfMeta.get("step", "")
        return self.__currentStep

    def getCurrentStepLabel(self):
        if self.__currentStepLabel is None:
            wfMeta = self._getWorkflowMetadata()
            self.__currentStepLabel = wfMeta.get("label", "")
        return self.__currentStepLabel

    def getNextStepAcceptMessage(self):
        step = self.getCurrentStep()
        msg = "?"
        if step=="inbox":
            msg = "This record is ready for the <strong>Investigation</strong> stage."
        elif step=="investigation":
            msg = "This record is ready for the <strong>Metadata Review</strong> stage."
        elif step=="metadata-review":
            msg = "This record is ready for the <strong>Final Review</strong> stage."
        elif step=="final-review":
            msg = "This record is ready to be <strong>Published</strong>."
        elif step=="live":
            msg = "This record has already been <strong>Published</strong>."
        return msg

    def getNextStepAcceptValidationErrorMessage(self):
        step = self.getCurrentStep()
        msg = "?"
        if step=="pending":
            msg = "You must accept responsibility and accountability for the" + \
            " accuracy and completeness of the information provided before" + \
            " you can submit this item!"
        elif step=="reviewing":
            msg = "You must check the 'Make record live' checkbox!"
        elif step=="live":
            msg = "[Live]"
        return msg

    def getJsonMetadata(self):              # used
        d = self.__tfpackage
        d["dc:title"]=d.get("title", "") or d.get("dc:title", "")
        d["dc:abstract"]=d.get("description", "") or d.get("dc:abstract", "")
        return jsonWriter(self.__tfpackage)

    def getAttachedFiles(self):
        req = SearchRequest("attached_to:%s" % self.__oid)
        req.setParam("rows", "1000")
        out = ByteArrayOutputStream()
        Services.indexer.search(req, out)
        result = JsonConfigHelper(ByteArrayInputStream(out.toByteArray()))
        sr = jsonReader(result.toString())
        docs = sr.get("response", {}).get("docs", [])
        docs = [{
                      "filename":d["filename"][0],
                      "attachment_type":d["attachment_type"][0],
                      "access_rights":d["access_rights"][0],
                      "id":d["id"]
                } for d in docs]
        docs.sort(lambda a, b: cmp(a["filename"], b["filename"]))
        return jsonWriter(docs)

    def getAjaxRequestUrl(self):
        return "../workflows/test.ajax"

    def getJsonTest(self):                  # used (testing)
        return jsonWriter("""Testing a string with ' and " and \n\rnewlines""")

    def getJsonPackagedItems(self):
        return jsonWriter(self._getPackagedItems())

    def getFormData(self, field):
        formData = self.vc("formData")
        #print "getFormData(field='%s')='%s'" % (field, formData.get(field, ""))
        return StringEscapeUtils.escapeHtml(formData.get(field, ""))

    def getOid(self):
        print "getOid()='%s'" % self.__oid
        return self.__oid

    def getSearchResults(self, query=None, pageNum=1):
#        ##
#        import search
#        # setup the context
#        for name in bindings.keySet():
#            search.__dict__[name] = bindings.get(name)
#        #sData = search.SearchData()
#        ##
        portal = self.Services.portalManager.get(portalId)
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
        print "req='%s'" % req.toString()
        out = ByteArrayOutputStream()
        self.Services.indexer.search(req, out)
        writer = StringWriter()
        IOUtils.copy(ByteArrayInputStream(out.toByteArray()), writer)
        jsonStr = writer.toString()
        #json = jsonReader(jsonStr)
        return jsonStr

        if False:
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

    def _getPackagedItemsData(self):
        print "_getPackagedItemsData()"
        maxPerRequest = 20  # get max of 20 at a time
        packagedIds = []
        docs = []
        fields="id,dc_description,dc_title,dc_format,display_type,preview,thumbnail"
        #fields+=",owner,security_filter"
        try:
            for i in self.__manifest.itervalues():
                packagedIds.append(i["id"])
            def idsSearch(ids):
                query = " ".join(["id:"+id for id in ids])
                req = SearchRequest(query)
                #req.setParam("wt", "json") # already set
                req.setParam("fl", fields)
                req.setParam("rows", str(maxPerRequest*4))
                #print "req='%s'" % req.toString()
                out = ByteArrayOutputStream()
                self.Services.indexer.search(req, out)
                writer = StringWriter()
                IOUtils.copy(ByteArrayInputStream(out.toByteArray()), writer)
                jsonStr = writer.toString()
                json = jsonReader(jsonStr)
                docs = json.get("response",{"docs":[]}).get("docs", [])
                return docs
            for x in xrange(0, len(packagedIds), maxPerRequest):
                ds = idsSearch(packagedIds[x:x+maxPerRequest])
                docs.extend(ds)
            docs.sort(lambda a, b: cmp(a["dc_title"][0], b["dc_title"][0]))
            if len(docs)!=len(packagedIds):
                print "Warning: packagedIds=%s but received %s docs" % (len(packagedIds), len(docs))
        except Exception, e:
            print "_getPackagedItemsData() error: '%s'" % str(e)
        return docs

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

    def _setItemRepresentation(self, id, title, representation):
        try:
            #print "**** _setItemRepresentation(id='%s', title='%s', representation='%s')" % (id, title, representation)
            nodeId = "node-%s" % id
            if not self.__manifest.has_key(nodeId):
                self.__manifest[nodeId] = {"id":id, "relationship":{}}
            node = self.__manifest[nodeId]
            node["title"]=title
            if(node.get("relationship") is None):
                node["relationship"]={}
            relationship = node.get("relationship")
            relationship["representation"]=representation
            self._savePackage()
            return self.__manifest.copy()
        except Exception, e:
            print "Error in _setItemRepresentation() - '%s'" % str(e)
            return {"error": "Failed to set representation! '%s'" % str(e)}

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
            self.Services.indexer.search(req, out)
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

    def _getObject(self):
        if not self.__object:
            try:
                #self.__object = Services.storage.getObject(self.__oid)
                self.__object = self.Services.storage.getObject(self.__oid)
            except StorageException, e:
                self.errorMsg = "Failed to retrieve object : " + e.getMessage()
                return None
        return self.__object

    def _getTFPackage(self):
        # get the TF package manifest
        tfpackage = None
        object = self._getObject()
        sourceId = object.getSourceId()
        payload = object.getPayload(sourceId)
        writer = StringWriter()
        IOUtils.copy(payload.open(), writer)
        tfpackage = jsonReader(writer.toString())
        payload.close()
        return tfpackage

    def _saveTFPackage(self, tfpackage):
        json = jsonWriter(tfpackage)
        object = self._getObject()
        object.updatePayload(object.getSourceId(),
                        ByteArrayInputStream(String(json).getBytes("UTF-8")))

    def _savePackage(self):
        self._saveTFPackage(self.__tfpackage)

    def _getWorkflowMetadata(self):
        wfMetadata = None
        object = self._getObject()
        try:
            payload = object.getPayload("workflow.metadata")
            writer = StringWriter()
            IOUtils.copy(payload.open(), writer)
            wfMetadata = jsonReader(writer.toString())
            payload.close()
        except StorageException, e:
            pass
        return wfMetadata

    def _saveWorkflowMetadata(self, wfMetadata):
        json = jsonWriter(wfMetadata)
        object = self._getObject()
        object.updatePayload("workflow.metadata",
                            ByteArrayInputStream(String(json).getBytes("UTF-8")))

    def _updatePackageMetadata(self, progressStep=False):
        print "** dataset update-package-meta **"
        result = {"error":"unknown"}
        currentStep = self.getCurrentStep()
        targetStep = None
        print "  currentStep='%s'" % currentStep
        if currentStep=="":
            # if currentStep=="" then creating a new collection!
            print "****** Creating a new Collection ******"
            print "????????????????????????????????????????"
            # check security
        try:
            doc = {}
            docs = self.__getSolrData(self.__oid).get("response", {}).get("docs", [])
            if len(docs):
                doc = docs[0]
            workflowStep = doc.get("workflow_step")[0]
            if workflowStep!=currentStep:
                print "*** Warning: workflow_step != currentStep ('%s'!='%s')!" % \
                        (workflowStep, currentStep)
            workflowSecurity = doc.get("workflow_security", [])
            json = self.vc("systemConfig")
            jsonConfigFile = json.getMap(
                    "portal/packageTypes/dataset").get("jsonconfig")
            jsonConfigFile = FascinatorHome.getPathFile(
                    "harvest/workflows/" + jsonConfigFile)
            f = open(jsonConfigFile.toString(), "r")
            try:
                config = jsonReader(f.read())
            finally:
                f.close()
            stages = config.get("stages")
            currentStage = None
            nextStage = None
            nextStep = None
            for stage in stages:
                if currentStage:
                    nextStage = stage
                    nextStep = nextStage.get("name")
                    break
                if stage.get("name")==currentStep:
                    currentStage = stage
            #if currentStep=="":
            #    nextStep = stages[0]
            #    nextStep = nextStage.get("name")
            username = self.username()
            userRoles = self.userRoles()
            print "username='%s'" % username
            print "userRoles='%s'" % userRoles
            owner = doc.get("owner")
            #print "workflow_security='%s'" % workflowSecurity
            #print "security_filter='%s'" % doc.get("security_filter")
            #object = self._getObject()
            #metadata = object.getMetadata()
            #owner = metadata.getProperty("owner")
            print "nextStep='%s'" % nextStep
            print "owner='%s'" % owner
            if progressStep:
                targetStep = nextStep
                print "  targetStep='%s'" % targetStep
                #return  {"error":"Just testing (next step='%s')" % nextStep}
            if (currentStep=="pending") and (owner!=username) and ("admin" not in userRoles):
                print "*** Not the owner of this object or an admin"
                return {"error":"Only the owner or admin can do this!"}
            if (currentStep=="reviewing") and ("admin" not in userRoles) and \
                    (not set(userRoles).intersection(workflowSecurity)):
                print "*** Not an admin or you do not have the correct role"
                return {"error":"Not an admin or you do not have the correct role"}
            if (currentStep=="live") and ("admin" not in userRoles) and \
                    (not set(userRoles).intersection(workflowSecurity)):
                print "*** Not an admin or you do not have the correct role"
                return {"error":"Not an admin or you do not have the correct role"}
        except Exception, e:
            print "Error in _updatePackageMetadata(): '%s'" % str(e)
            return {"error":str(e)}
        #
        formData = self.__formData
        tfpackage = self.__tfpackage
        try:
            metaList = list(formData.getValues("metaList[]"))
            #print "++metaList='%s'" % str(metaList)
            removedSet = set(tfpackage.get("metaList", [])).difference(metaList)
            try:
                for metaName in metaList:
                    value = formData.get(metaName)
                    tfpackage[metaName] = value
                tfpackage["metaList"] = metaList
                for metaName in removedSet:
                    del tfpackage[metaName]
            except Exception, e:
                print "Error: '%s'" % str(e)
            tfpackage["title"]=tfpackage.get("dc:title", "")
            tfpackage["description"]=tfpackage.get("dc:description", "")
            title = tfpackage["title"]
            if not title:
                print "*** no title ***"
                #print dir(formData)
                #print formData.formFields
                #print formData.getValues("metaList")
                return {"error":"no title"}
            ##
            try:
                wfMeta = self._getWorkflowMetadata()
                if targetStep:
                    wfMeta["targetStep"] = targetStep
                print "title='%s'" % title
                print "wfMeta='%s'" % wfMeta
                formData2 = wfMeta.get("formData")
                if formData2 is None:
                    formData2 = {}
                    wfMeta["formData"]=formData2
                formData2["title"]=title
                formData2["description"]=tfpackage["description"]
                self._saveWorkflowMetadata(wfMeta)
            except Exception, e:
                print "  ERROR: %s" % str(e)
            # Save & re-index
            self._saveTFPackage(tfpackage)
            self._reIndex(targetStep)  # Re-index - for title|description changes
            if targetStep:
                # progress all attachments as well
                pass
            result = {"ok":"updated ok", "oid":self.__oid}
        except Exception, e:
            print "*** error: %s" % str(e)
            result = {"error":str(e)}
        return result

    def _reIndex(self, step):
        object = self._getObject()

        # transform the object to other datastream e.g. dublin core, rif-cs and vitro
        try:
            simpleConfig = JsonSimpleConfig()
            jsonVelocityTransformer = PluginManager.getTransformer("jsonVelocity")
            print " *** jsonVelocityTransformer: ", jsonVelocityTransformer
            jsonVelocityTransformer.init(simpleConfig.getSystemFile())
            jsonVelocityTransformer.transform(object, "{}")
        except TransformerException, e:
            print "Fail to transform object using JsonVelocityTransformer: ", str(e)

        oid = object.getId()
        self.Services.indexer.index(oid)
        self.Services.indexer.commit()
        self.sendMessage(oid, step)

    def __getSolrData(self, oid):
        #print "__getSolrData()"
        resultDict = {}
        try:
            portal = self.page.getPortal()
            query = 'id:"%s"' % oid
            req = SearchRequest(query)
            req.addParam("fq", 'item_type:"object"')
            out = ByteArrayOutputStream()
            self.Services.getIndexer().search(req, out)
            writer = StringWriter()
            IOUtils.copy(ByteArrayInputStream(out.toByteArray()), writer)
            resultDict = jsonReader(writer.toString())
        except Exception, e:
            print "Error in __getSolrData(): '%s'" % str(e)
        return resultDict

    def sendMessage(self, oid, step):
        param = {}
        param["oid"] = oid
        if step is None:
            param["eventType"] = "ReIndex"
        else:
            param["eventType"] = "NewStep : %s" % step
        param["username"] = self.vc("page").authentication.get_username()
        param["context"] = "Workflow"
        self.messaging.onEvent(param)
