import md5, uuid

from com.googlecode.fascinator.common import Manifest

from java.io import ByteArrayInputStream
from java.lang import String

from org.apache.commons.lang import StringEscapeUtils

class ManifestData:
    def __init__(self):
        pass

    def __activate__(self, context):
        self.velocityContext = context
        self.fd = self.vc("formData").get

        #print "formData=%s" % self.vc("formData")
        result = "{}"
        func = self.fd("func")
        oid = self.fd("oid")

        self.__object = Services.getStorage().getObject(oid)
        self.packagePid = None
        pidList = self.__object.getPayloadIdList()
        for pid in pidList:
            if pid.endswith(".tfpackage"):
                self.packagePid = pid
        payload = self.__object.getPayload(self.packagePid)
        self.__manifest = Manifest(payload.open())
        payload.close()

        # Add a new custom node at the top leve
        if func == "add-custom":
            id = md5.new(str(uuid.uuid4())).hexdigest()
            self.__manifest.addTopNode(id, "Untitled")
            # We gave an ID for the Library to use in storage, but as
            #  metadata we want it to say 'blank'
            node = self.__manifest.getNode("node-%s" % id)
            node.setId("blank")
            print "Adding blank node: '%s'" % id
            self.__saveManifest()
            result = '{ "attributes": { "id": "node-%s", "rel": "blank" }, "data": "Untitled" }' % id

        # Update top-level package metadata
        if func == "update-package-meta":
            metaList = list(self.vc("formData").getValues("metaList"))
            jsonObj = self.__manifest.getJsonObject()
            for metaName in metaList:
                value = self.fd(metaName)
                jsonObj.put(metaName, value)
            #title = formData.get("title")
            #self.__manifest.set("title", StringEscapeUtils.escapeHtml(title))
            self.__saveManifest()

        # Rename the indicated node
        if func == "rename":
            node = self.__manifest.getNode(self.fd("nodeId"))
            node.setTitle(self.fd("title"))
            self.__saveManifest()

        # Move a node from one location to another
        elif func == "move":
            moveType = self.fd("type")
            if moveType == "before":
                self.__manifest.moveBefore(self.fd("nodeId"), self.fd("refNodeId"))
            elif moveType == "after":
                self.__manifest.moveAfter(self.fd("nodeId"), self.fd("refNodeId"))
            elif moveType == "inside":
                self.__manifest.move(self.fd("nodeId"), self.fd("refNodeId"))
            self.__saveManifest()

        # Update the metadata of the indicated node
        elif func == "update":
            title = StringEscapeUtils.escapeHtml(self.fd("title"))
            hidden = self.fd("hidden")
            hidden = hidden == "true"

            node = self.__manifest.getNode(self.fd("nodeId"))
            node.setTitle(title)
            node.setHidden(hidden)
            self.__saveManifest()
            result = '{ "title": "%s", "hidden": "%s" }' % (title, hidden)

        # Update the metadata of the indicated node
        elif func == "delete":
            node = self.__manifest.getNode(self.fd("nodeId"))
            title = node.getTitle()
            if title:
                self.__manifest.delete(self.fd("nodeId"))
                self.__saveManifest()
            else:
                title = "Untitled"
            result = '{ "title": "%s" }' % title
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

    def __saveManifest(self):
        manifestStr = String(self.__manifest.toString(True))
        self.__object.updatePayload(self.packagePid,
                        ByteArrayInputStream(manifestStr.getBytes("UTF-8")))
