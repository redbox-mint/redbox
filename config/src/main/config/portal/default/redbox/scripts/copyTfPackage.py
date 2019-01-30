import re

from com.googlecode.fascinator.api.storage import StorageException
from java.util import Date
from java.util import Calendar
from java.lang import String
from com.googlecode.fascinator.common import JsonObject
from java.util import HashMap
from java.util import ArrayList
from java.util import Collections
from com.googlecode.fascinator.portal.report import RedboxReport
from org.apache.commons.io import FileUtils
from java.io import File
from com.googlecode.fascinator.common import FascinatorHome
from com.googlecode.fascinator.common.storage import StorageUtils
from com.googlecode.fascinator.portal.services import OwaspSanitizer
from org.apache.commons.lang import StringEscapeUtils
from org.apache.commons.lang import StringUtils
from org.apache.commons.io import IOUtils
from com.googlecode.fascinator.common import JsonSimple
from org.json.simple import JSONArray
from java.io import ByteArrayInputStream
from java.io import ByteArrayOutputStream
from com.googlecode.fascinator.common.messaging import MessagingServices
from com.googlecode.fascinator.messaging import TransactionManagerQueueConsumer


class CopyTfPackageData:

    def __init__(self):
        self.messaging = MessagingServices.getInstance()

    def __activate__(self, context):
        self.auth = context["page"].authentication
        self.errorMsg = ""
        self.request = context["request"]
        self.response = context["response"]
        self.formData = context["formData"]
        self.storage = context["Services"].getStorage()

        self.log = context["log"]
        self.reportManager = context["Services"].getService("reportManager")

        fromOid = self.formData.get("fromOid")
        fromObject = self.storage.getObject(fromOid)

        if (self.auth.is_logged_in()):
            if (self.auth.is_admin() == True):
                pass
            elif (self.__isOwner(fromObject)):
                pass
            else:
                self.errorMsg = "Requires Admin / Librarian / Reviewer / owner access."
        else:
            self.errorMsg = "Please login."
        if self.errorMsg == "":
            toOid = self.formData.get("toOid")
            toObject = self.storage.getObject(toOid)
            storeRelatedData = self.formData.get("relatedData")
            fromTFPackage = self._getTFPackage(fromObject)
            toTFPackage = self._getTFPackage(toObject)
            # get relevant dc:description from new object before you overwrite it with 'from' data, as this should exist from form data created in initial object packaging (packaging.py)
            toTFPackageJson = JsonSimple(toTFPackage.open()).getJsonObject()
            relevant_description = toTFPackageJson.get("dc:description")
            fromInputStream = fromTFPackage.open()
            try:
                StorageUtils.createOrUpdatePayload(toObject, toTFPackage.getId(), fromInputStream)
            except StorageException:
                print "error setting tfPackage"
            finally:
                fromTFPackage.close()

            tfMetaPropertyValue = self.formData.get("tfMetaPropertyValue")
            if tfMetaPropertyValue == 'dmpToSelfSub':
                # fetch recently created new 'to' object from storage to get all data
                toTFPackage = self._getTFPackage(toObject)
                toTFPackageJson = JsonSimple(toTFPackage.open()).getJsonObject()
                self.setMultiDescription(toTFPackageJson, relevant_description)
                inStream = IOUtils.toInputStream(toTFPackageJson.toJSONString(), "UTF-8")
                try:
                    StorageUtils.createOrUpdatePayload(toObject, toTFPackage.getId(), inStream)
                except StorageException:
                    print "error setting description text in tfPackage"
                finally:
                    inStream.close()
                self.log.info(
                    "Completed migrating 'dc:description' to dc:decription.1.text' for oid: %s." % toTFPackage.getId())
                self.log.debug("Result: %r" % toTFPackageJson)

            fromTFPackageJson = JsonSimple(fromTFPackage.open()).getJsonObject()
            self.log.debug('from json is: %r' % fromTFPackageJson)
            if storeRelatedData != "false":
                # add relatedOid info
                fromTFPackageJson = self._addRelatedOid(JsonSimple(fromTFPackage.open()), toOid)

            self.log.debug('from tfPackage json is now: %r' % fromTFPackageJson)
            inStream = IOUtils.toInputStream(fromTFPackageJson.toJSONString(), "UTF-8")

            try:
                StorageUtils.createOrUpdatePayload(fromObject, fromTFPackage.getId(), inStream)
            except StorageException:
                print "error setting tfPackage"
            finally:
                inStream.close()

            self._addPropertyValueToTFMeta(toObject, tfMetaPropertyValue)

            self._reharvestPackage()

            result = '{"status": "ok", "url": "%s/workflow/%s", "oid": "%s" }' % (context["portalPath"], toOid, toOid)
        else:
            result = '{"status": "err", "message": "%s"}' % self.errorMsg
        writer = self.response.getPrintWriter("application/json; charset=UTF-8")
        writer.println(result)
        writer.close()

    def getErrorMsg(self):
        return self.errorMsg

    def _reharvestPackage(self):
        message = JsonObject()
        message.put("oid", self.formData.get("toOid"))
        message.put("task", "reharvest")
        self.messaging.queueMessage(TransactionManagerQueueConsumer.LISTENER_ID, message.toString())

    def _addPropertyValueToTFMeta(self, object, tfMetaPropertyValue):
        objectMetadata = object.getMetadata()
        objectMetadata.setProperty("copyTFPackage", tfMetaPropertyValue)
        objectMetadata.setProperty("render-pending", "true")

        output = ByteArrayOutputStream();
        objectMetadata.store(output, None);
        input = ByteArrayInputStream(output.toByteArray());
        StorageUtils.createOrUpdatePayload(object, "TF-OBJ-META", input);

    def _addRelatedOid(self, tfPackageJson, relatedOid):
        relatedOids = tfPackageJson.getArray("related.datasets")
        if relatedOids is None:
            relatedOids = JSONArray()

        relatedOidJsonObject = JsonObject()
        relatedOidJsonObject.put("oid", relatedOid)
        relatedOids.add(relatedOidJsonObject)
        jsonObject = tfPackageJson.getJsonObject()
        jsonObject.put("related.datasets", relatedOids)
        return jsonObject

    # Retrieve and parse the Fascinator Package from storage
    def _getTFPackage(self, object):
        # We don't need to worry about close() calls here
        try:
            sourceId = object.getSourceId()
            payload = None
            if sourceId is None or not sourceId.endswith(".tfpackage"):
                # The package is not the source... look for it
                for pid in object.getPayloadIdList():
                    if pid.endswith(".tfpackage"):
                        payload = object.getPayload(pid)
                        payload.setType(PayloadType.Source)
            else:
                payload = object.getPayload(sourceId)

            return payload

        except Exception, e:
            self.log.error("Error during package access", e)
            return None

        return None

    def __isOwner(self, sourceObj):
        try:
            owner = sourceObj.getMetadata().getProperty("owner")
            return owner == self.auth.get_username()

        except Exception, e:
            self.log.error("Error during changing ownership of data. Exception: " + str(e))
            return False

    def setMultiDescription(self, tfPackageJson, descriptionValue):
        if descriptionValue is None:
            self.log.info("No description found. Aborting set description shadow...")
            tfPackageJson.put("dc:description.1.text", "")
            tfPackageJson.put("dc:description.1.shadow", "")
            tfPackageJson.put("dc:description.1.type", "full")
            return
        else:
            ## no tags are added to wysiwyg until user interacts with wysiwyg editor
            unescapedDescription = ""
            escapedDescription = ""
            rawDescription = StringUtils.defaultString("%s" % descriptionValue)
            ## sanitize the incoming description
            self.log.debug("raw deprecated description is: %s" % rawDescription)
            sanitizedDescription = OwaspSanitizer.sanitizeHtml("dc:description.1.text", rawDescription)
            if (sanitizedDescription):
                # not completely accurate for checking for tags but ensures a style consistent with wysiwyg editor
                if re.search("^<p>.*</p>|^&lt;p&gt;.*&lt;\/p&gt;", sanitizedDescription):
                    ## deprecated description may be unescaped or escaped already - so ensure both cases covered
                    unescapedDescription = StringEscapeUtils.unescapeHtml("%s" % sanitizedDescription)
                    escapedDescription = OwaspSanitizer.escapeHtml("%s" % sanitizedDescription)
                else:
                    unescapedDescription = StringEscapeUtils.unescapeHtml("<p>%s</p>" % sanitizedDescription)
                    escapedDescription = OwaspSanitizer.escapeHtml("<p>%s</p>" % sanitizedDescription)
            self.log.info("relevant unescaped description is: %s" % unescapedDescription)
            self.log.info("relevant escaped description is: %s" % escapedDescription)
            tfPackageJson.put("dc:description.1.text", unescapedDescription)
            tfPackageJson.put("dc:description.1.shadow", escapedDescription)
            tfPackageJson.put("dc:description.1.type", "full")
            self.log.debug("Removing deprecated 'dc:description' key...")
            tfPackageJson.remove("dc:description")
            self.log.debug(
                "Completed migrating 'dc:description' to dc:description.1.text|shadow" % tfPackageJson)
