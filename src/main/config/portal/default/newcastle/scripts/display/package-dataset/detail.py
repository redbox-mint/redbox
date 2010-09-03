
from java.io import ByteArrayInputStream
from java.io import StringWriter
from java.lang import String
from org.apache.commons.lang import StringEscapeUtils
from org.apache.commons.io import IOUtils

from json2 import read as jsonReader, write as jsonWriter


class DetailData:
    def __init__(self):
        pass

    def __activate__(self, context):
        print "****************************"
        print "__activate__()"
        print "****************************"
        self.velocityContext = context
        self.fd = self.vc("formData").get
        oid = self.fd("oid")
        print "-detail.py oid='%s'" % oid

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
    