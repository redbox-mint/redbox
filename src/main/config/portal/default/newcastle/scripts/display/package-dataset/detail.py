
from java.io import ByteArrayInputStream
from java.io import StringWriter
from java.lang import String
from java.util import HashMap, TreeMap
from org.apache.commons.lang import StringEscapeUtils
from org.apache.commons.io import IOUtils
from au.edu.usq.fascinator.common import JsonConfigHelper

from json2 import read as jsonReader, write as jsonWriter


class DetailData:
    def __init__(self):
        pass

    def __activate__(self, context):
        print "****************************"
        print "__activate__()"
        print "****************************"
        self.velocityContext = context
        metadata = context.get("metadata")
        self.oid = metadata.get("id")
        print "-detail.py id='%s'" % self.oid
        self.Services = context.get("Services")

    def escape(self, text):
        return StringEscapeUtils.escapeHtml(text)

    # Get from velocity context
    def vc(self, index):
        if self.velocityContext[index] is not None:
            return self.velocityContext[index]
        else:
            log.error("ERROR: Requested context entry '" + index + "' doesn't exist")
            return None

    def getTest(self):
        return "-Just testing-"

    def getMetadata(self):      # tfpackage
        object = self.Services.getStorage().getObject(self.oid)
        sourceId = object.getSourceId()
        payload = object.getPayload(sourceId)
        #self.manifest = JsonConfigHelper(payload.open())
        writer = StringWriter()
        IOUtils.copy(payload.open(), writer)
        tfpackage = jsonReader(writer.toString())
        payload.close()
        return tfpackage

    def getMetadataList(self):
        l = []
        metadata = self.getMetadata()
        if metadata.has_key("metaList"):
            metadata.pop("metaList")
        for k, v in metadata.iteritems():
            l.append("%s = '%s'" % (k,v))
        l.sort()
        return l

    def getList(self, baseKey):
        if baseKey[-1:] != ".":
            baseKey = baseKey + "."
        valueMap = TreeMap()
        metadata = self.getMetadata()
        for key in [k for k in metadata.keys() if k.startswith(baseKey)]:
            value = metadata.get(key)
            field = key[len(baseKey):]
            index = field[:field.find(".")]
            #print "%s. '%s' = '%s'" % (index, key, value)
            data = valueMap.get(index)
            if not data:
                data = HashMap()
                valueMap.put(index, data)
            data.put(field[field.find(".")+1:], value)
        return valueMap

