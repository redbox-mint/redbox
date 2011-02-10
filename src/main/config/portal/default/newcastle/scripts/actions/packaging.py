import md5, uuid

from au.edu.usq.fascinator import HarvestClient
from au.edu.usq.fascinator.api.storage import StorageException
from au.edu.usq.fascinator.common import FascinatorHome, JsonConfigHelper, JsonConfig
from au.edu.usq.fascinator.common.storage import StorageUtils

from java.io import File, FileOutputStream, InputStreamReader, OutputStreamWriter
from java.lang import Exception

from org.apache.commons.io import FileUtils, IOUtils

class PackagingData:

    def __init__(self):
        pass

    def __activate__(self, context):
        self.velocityContext = context

        print "formData=%s" % self.vc("formData")

        result = "{}"
        func = self.vc("formData").get("func")
        if func == "create-new":
            result = self.__createNew()
        elif func == "create-from-selected":
            result = self.__createFromSelected()
        elif func == "update":
            result = self.__update()
        elif func == "clear":
            result = self.__clear()
        elif func == "modify":
            result = self.__modify()
        elif func == "add-custom":
            result = self.__addCustom()

        writer = self.vc("response").getPrintWriter("application/json; charset=UTF-8")
        writer.println(result)
        writer.close()

    # Get from velocity context
    def vc(self, index):
        if self.velocityContext[index] is not None:
            return self.velocityContext[index]
        else:
            log.error("ERROR: Requested context entry '" + index + "' doesn't exist")
            return None

    def __createNew(self):
        print "Creating a new package..."
        packageType, jsonConfigFile = self.__getPackageTypeAndJsonConfigFile()
        print "packageType='%s'" % packageType
        print "jsonConfigFile='%s'" % jsonConfigFile

        manifestHash = "%s.tfpackage" % uuid.uuid4()
        # store the manifest file for harvesting
        packageDir = FascinatorHome.getPathFile("packages")
        packageDir.mkdirs()
        manifestFile = File(packageDir, manifestHash)
        outStream = FileOutputStream(manifestFile)
        outWriter = OutputStreamWriter(outStream, "UTF-8")

        self.vc("sessionState").set("package/active", None)
        manifest = self.__getActiveManifest()
        manifest.set("packageType", packageType)

        metaList = self.vc("formData").getValues("metaList")
        if metaList is None:
            metaList = self.vc("formData").getValues("metaList[]")
        if metaList is None:
            metaList = []
        for metaName in list(metaList):
            value = self.vc("formData").get(metaName)
            manifest.set(metaName, value)
        #
        print "------"
        print manifest
        print "------"
        manifest.store(outWriter, True)
        outWriter.close()

        try:
            # harvest the package as an object
            username = self.vc("sessionState").get("username")
            if username is None:
                username = "guest" # necessary?
            harvester = None
            # set up config files, creating if necessary
            workflowsDir = FascinatorHome.getPathFile("harvest/workflows")
            configFile = self.__getFile(workflowsDir, jsonConfigFile)
            self.__getFile(workflowsDir, "packaging-rules.py")
            # run the harvest client with our packaging workflow config
            harvester = HarvestClient(configFile, manifestFile, username)
            harvester.start()
            manifestId = harvester.getUploadOid()
            harvester.shutdown()
        except Exception, ex:
            error = "Packager workflow failed: %s" % str(ex)
            log.error(error, ex)
            if harvester is not None:
                harvester.shutdown()
            return '{ status: "failed" }'
        # clean up
        self.__clear()
        # return url to workflow screen
        return '{"status": "ok", "url": "%s/workflow/%s" }' % (portalPath, manifestId)


    def __createFromSelected(self):
        print "Creating package from selected..."
        packageType, jsonConfigFile = self.__getPackageTypeAndJsonConfigFile()
        #print "packageType='%s'" % packageType
        #print "jsonConfigFile='%s'" % jsonConfigFile

        # if modifying existing manifest, we already have an identifier,
        # otherwise create a new one
        manifestId = self.__getActiveManifestId()
        if manifestId is None:
            manifestHash = "%s.tfpackage" % uuid.uuid4()
        else:
            manifestHash = self.__getActiveManifestPid()

        # store the manifest file for harvesting
        packageDir = FascinatorHome.getPathFile("packages")
        packageDir.mkdirs()
        manifestFile = File(packageDir, manifestHash)
        outStream = FileOutputStream(manifestFile)
        outWriter = OutputStreamWriter(outStream, "UTF-8")
        manifest = self.__getActiveManifest()
        manifest.set("packageType", manifest.get("packageType", packageType))
        #print manifest
        #print "----"
        manifest.store(outWriter, True)
        outWriter.close()

        try:
            if manifestId is None:
                # harvest the package as an object
                username = self.vc("sessionState").get("username")
                if username is None:
                    username = "guest" # necessary?
                harvester = None
                # set up config files, and make sure they are both deployed
                workflowsDir = FascinatorHome.getPathFile("harvest/workflows")
                configFile = self.__getFile(workflowsDir, jsonConfigFile)
                rulesFile = self.__getFile(workflowsDir, "packaging-rules.py")
                # run the harvest client with our packaging workflow config
                harvester = HarvestClient(configFile, manifestFile, username)
                harvester.start()
                manifestId = harvester.getUploadOid()
                harvester.shutdown()
            else:
                # update existing object
                object = StorageUtils.getDigitalObject(Services.getStorage(), manifestId)
                manifestStream = FileUtils.openInputStream(manifestFile)
                StorageUtils.createOrUpdatePayload(object, manifestHash, manifestStream)
                manifestStream.close()
                object.close()
        except Exception, ex:
            error = "Packager workflow failed: %s" % str(ex)
            log.error(error, ex)
            if harvester is not None:
                harvester.shutdown()
            return '{ status: "failed" }'
        # clean up
        ##manifestFile.delete()
        self.__clear()
        # return url to workflow screen
        return '{ status: "ok", url: "%s/workflow/%s" }' % (portalPath, manifestId)

    def __update(self):
        print "Updating package selection..."
        activeManifest = self.__getActiveManifest()
        added = self.vc("formData").getValues("added")
        if added:
            titles = self.vc("formData").getValues("titles")
            for i in range(len(added)):
                id = added[i]
                title = titles[i]
                node = activeManifest.get("manifest//node-%s" % id)
                if node is None:
                    print "adding:", id, title.encode("UTF-8")
                    activeManifest.set("manifest/node-%s/id" % id, id)
                    activeManifest.set("manifest/node-%s/title" % id, title)
                else:
                    print "%s already exists" % id
        removed = self.vc("formData").getValues("removed")
        if removed:
            for id in removed:
                node = activeManifest.get("manifest//node-%s" % id)
                if node is not None:
                    print "removing:", id
                    activeManifest.removePath("manifest//node-%s" % id)
        print "activeManifest: %s" % activeManifest
        return '{ count: %s }' % self.__getCount()

    def __clear(self):
        print "Clearing package selection..."
        self.vc("sessionState").remove("package/active")
        self.vc("sessionState").remove("package/active/id")
        self.vc("sessionState").remove("package/active/pid")
        return "{}"

    def __modify(self):
        print "Set active package..."
        oid = self.vc("formData").get("oid")
        try:
            object = Services.getStorage().getObject(oid)
            sourceId = object.getSourceId()
            payload = object.getPayload(sourceId)
            payloadReader = InputStreamReader(payload.open(), "UTF-8")
            manifest = JsonConfigHelper(payloadReader)
            payloadReader.close()
            payload.close()
            object.close()
            self.vc("sessionState").set("package/active", manifest)
            self.vc("sessionState").set("package/active/id", oid)
            self.vc("sessionState").set("package/active/pid", sourceId)
        except StorageException, e:
            self.vc("response").setStatus(500)
            return '{ error: %s }' % str(e)
        return '{ count: %s }' % self.__getCount()

    def __getPackageTypeAndJsonConfigFile(self):
        try:
            packageType = self.vc("formData").get("packageType", "default")
            if packageType == "":
                packageType = "default"
            json = JsonConfigHelper(JsonConfig.getSystemFile())
            pt = json.getMap("portal/packageTypes/" + packageType)
            jsonConfigFile = pt.get("jsonconfig")
            if jsonConfigFile is None:
                jsonConfigFile = "packaging-config.json"
        except Exception, e:
            jsonConfigFile = "packaging-config.json"
        return (packageType, jsonConfigFile)

    def __addCustom(self):
        id = md5.new(str(uuid.uuid4())).hexdigest()
        return '{ attributes: { id: "node-%s", rel: "blank" }, data: "Untitled" }' % id

    def __getActiveManifestId(self):
        return self.vc("sessionState").get("package/active/id")

    def __getActiveManifestPid(self):
        return self.vc("sessionState").get("package/active/pid")

    def __getActiveManifest(self):
        activeManifest = self.vc("sessionState").get("package/active")
        if not activeManifest:
            activeManifest = JsonConfigHelper()
            activeManifest.set("title", "New package")
            activeManifest.set("viewId", portalId)
            self.vc("sessionState").set("package/active", activeManifest)
        return activeManifest

    def __getCount(self):
        count = self.__getActiveManifest().getList("manifest//id").size()
        print "count:", count
        return count

    def __getFile(self, packageDir, filename):
        file = File(packageDir, filename)
        if not file.exists():
            out = FileOutputStream(file)
            IOUtils.copy(Services.getClass().getResourceAsStream("/workflows/" + filename), out)
            out.close()
        return file