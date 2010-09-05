from au.edu.usq.fascinator.common import JsonConfigHelper

from java.io import ByteArrayInputStream
from java.lang import String
from org.apache.commons.lang import StringEscapeUtils

from json2 import read as jsonReader, write as jsonWriter


class ManifestData:
    def __init__(self):
        pass

    def __activate__(self, context):
        self.velocityContext = context
        self.fd = self.vc("formData").get
        formData = self.vc("formData")

        #print "formData=%s" % self.vc("formData")
        result = "{}"
        func = self.fd("func")
        oid = self.fd("oid")

        if func != "update-package-meta":
            nodeId = self.fd("nodeId")
            nodePath = self.__getNodePath(self.fd("parents"), nodeId)
            originalPath = "manifest//%s" % nodeId

        self.__object = Services.getStorage().getObject(oid)
        sourceId = self.__object.getSourceId()
        payload = self.__object.getPayload(sourceId)
        self.__manifest = JsonConfigHelper(payload.open())
        payload.close()

        if func == "update-package-meta":
            print "*********  update-package-meta ***************"
            tfpackage = jsonReader(str(self.__manifest))                            ##
            metaList = list(self.vc("formData").getValues("metaList"))
            removedSet = set(tfpackage.get("metaList", [])).difference(metaList)    ##
            try:
                for metaName in metaList:
                    value = self.fd(metaName)
                    ##self.__manifest.set(metaName, value)
                    tfpackage[metaName] = value                                         ##
                tfpackage["metaList"] = metaList                                        ##
                for metaName in removedSet:                                             ##
                    del tfpackage[metaName]                                             ##
            except Exception, e:
                print "Error: '%s'" % str(e)                                        ##
            self.__manifest = JsonConfigHelper(jsonWriter(tfpackage))               ##
            self.__saveManifest()
            if True:
                print "* targetStep set to 'live'!"
                wfMeta = self.__getWorkflowMetadata()
                wfMeta.set("targetStep", "live")
                self.__setWorkflowMetadata(wfMeta)
            # Re-index the object  - for title|description changes                  ##
            Services.indexer.index(self.__object.getId())                           ##
            Services.indexer.commit()                                               ##
            result='{"ok":"saved ok"}';                                             ##
        if func == "rename":
            title = self.fd("title")
            self.__manifest.set("%s/title" % nodePath, title)
            self.__saveManifest()
        elif func == "move":
            refNodeId = self.fd("refNodeId")
            refNodePath = self.__getNodePath(self.fd("refParents"),
                                             self.fd("refNodeId"));
            moveType = self.fd("type")
            if moveType == "before":
                self.__manifest.moveBefore(originalPath, refNodePath)
            elif moveType == "after":
                self.__manifest.moveAfter(originalPath, refNodePath)
            elif moveType == "inside":
                self.__manifest.move(originalPath, nodePath)
            self.__saveManifest()
        elif func == "update":
            title = StringEscapeUtils.escapeHtml(self.fd("title"))
            hidden = self.fd("hidden")
            hidden = hidden == "true"
            self.__manifest.set("%s/title" % nodePath, title)
            self.__manifest.set("%s/hidden" % nodePath, str(hidden))
            #if self.__manifest.get("%s/id" % nodePath) is None:
            #    print "blank node!"
            self.__saveManifest()
            result = '{ title: "%s", hidden: "%s" }' % (title, hidden)
        elif func == "delete":
            title = self.__manifest.get("%s/title" % nodePath)
            if title:
                self.__manifest.removePath(nodePath)
                self.__saveManifest()
            else:
                title = "Untitled"
            result = '{ title: "%s" }' % title

        self.__object.close()
        writer = self.vc("response").getPrintWriter("text/plain; charset=UTF-8")
        writer.println(result)
        writer.close()

    # Get from velocity context
    def vc(self, index):
        if self.velocityContext[index] is not None:
            return self.velocityContext[index]
        else:
            log.error("ERROR: Requested context entry '" + index + "' doesn't exist")
            return None

    def __getNodePath(self, parents, nodeId):
        parents = [p for p in parents.split(",") if p != ""]
        nodePath = "manifest/%s" % nodeId
        if len(parents) > 0:
            nodePath = ""
            for parent in parents:
                if nodePath == "":
                    nodePath = "manifest/%s"  % parent
                else:
                    nodePath += "/children/%s" % parent
            nodePath += "/children/%s" % nodeId
        return nodePath

    def __saveManifest(self):
        manifestStr = String(self.__manifest.toString())
        self.__object.updatePayload(self.__object.getSourceId(),
                                    ByteArrayInputStream(manifestStr.getBytes("UTF-8")))

    def __getWorkflowMetadata(self):
        wfPayload = self.__object.getPayload("workflow.metadata")
        wfMeta = JsonConfigHelper(wfPayload.open())
        wfPayload.close()
        return wfMeta

    def __setWorkflowMetadata(self, metadata):
        try:
            jsonString = String(metadata.toString())
            inStream = ByteArrayInputStream(jsonString.getBytes("UTF-8"))
            self.__object.updatePayload("workflow.metadata", inStream)
            return True
        except StorageException, e:
            return False

