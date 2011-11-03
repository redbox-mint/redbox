from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.common import JsonObject
from com.googlecode.fascinator.common.messaging import MessagingServices
from com.googlecode.fascinator.common.solr import SolrResult
from com.googlecode.fascinator.messaging import TransactionManagerQueueConsumer

## Pick appropriately
# Fedora 2
#from fedora.client import FedoraClient
# Fedora 3
from org.fcrepo.client import FedoraClient

from java.io import ByteArrayInputStream
from java.io import ByteArrayOutputStream
from java.io import InputStreamReader
from java.lang import Exception

from org.dom4j import DocumentFactory
from org.dom4j.io import SAXReader

class VitalData:
    def __init__(self):
        self.messaging = MessagingServices.getInstance()

    def __activate__(self, context):
        self.vc = context
        self.config   = self.vc["systemConfig"]
        self.log      = self.vc["log"]
        self.services = self.vc["Services"]
        self.writer   = self.vc["response"].getPrintWriter("text/html; charset=UTF-8")

        # Working variables
        self.fedoraUrl = None
        self.docFactory = None
        self.saxReader = None

        self.process()

    def process(self):
        self.log.debug("VITAL housekeeping executing")

        # Find solr records
        result = self.search_solr()
        if result is None:
            return

        # Is there any work to do?
        num = result.getNumFound()
        if num == 0:
            self.writer.println("No records to process")
            self.writer.close()
            return

        # Time to connect to fedora
        fedora = self.fedora_connect()
        if fedora is None:
            return

        # Now loop through each object and process
        for record in result.getResults():
            success = self.process_record(record, fedora)
            if not success:
                return

        self.writer.println("%s record(s) processed" % num)
        self.writer.close()

    # Process an individual record
    def process_record(self, record, fedora):
        try:
            # Get the object from storage
            id = record.getFirst("storage_id")
            object = self.services.getStorage().getObject(id)

            # And get its metadata
            metadata = object.getMetadata()
            vitalPid = metadata.getProperty("vitalPid")
            if vitalPid is None:
                self.log.error("Object '{}' has invalid VITAL data", id)
                self.throw_error("Object '%s' has invalid VITAL data" % id)
                return False

            # Get handle in DC datastream from VITAL
            vitalHandle = self.get_handle(fedora, vitalPid)
            if vitalHandle is None:
                # Finish with failed access
                return False
            if vitalHandle == "NONE":
                # Finish with no error, but no handle (yet)
                self.log.debug("Object '{}', in VITAL '{}' has no handle yet", id, vitalPid)
                return True

            # We have a valid handle now, write to the object
            metadata.setProperty("vitalHandle", vitalHandle)
            object.close()

            # Transform the object, to update our payloads
            #transformer = PluginManager.getTransformer("jsonVelocity")
            #transformer.init(JsonSimpleConfig.getSystemFile())
            #transformer.transform(object, "{}")

            # Re-index... avoids showing up in this script again
            #self.services.getIndexer().index(id)
            #self.services.getIndexer().commit()

            # Finally send a message to the VITAL subscriber
            self.send_message(id)

            # Simple debugging
            self.log.debug("Processing: '{}' <= '{}'", vitalPid, id)
            self.log.debug("Handle: '{}'", vitalHandle)
            return True

        except Exception, e:
            self.log.error("Error updating object: ", e)
            self.throw_error("failure updating object: " + e.getMessage())
            return False

    # Send an event notification
    def send_message(self, oid):
        message = JsonObject()
        message.put("oid", oid)
        message.put("eventType", "ReIndex")
        message.put("username", "system")
        message.put("context", "Workflow")
        message.put("task", "workflow")
        message.put("quickIndex", True)
        self.messaging.queueMessage(
                TransactionManagerQueueConsumer.LISTENER_ID,
                message.toString())

    # Get the handle for the PID from VITAL, if set
    def get_handle(self, fedora, vitalPid):
        try:
            # Get and parse the XML
            if not self.fedoraUrl.endswith("/"):
                self.fedoraUrl += "/"
            url = self.fedoraUrl + "get/" + vitalPid + "/DC"
            self.log.debug("URL: '{}'", url)
            inStream = fedora.get(url, True)
            document = self.parse_xml(inStream)
            if document is None:
                return None

            # Does the DC have any identifiers yet?
            idNodes = document.selectNodes("//dc:identifier")
            if idNodes is None:
                return "NONE"

            # Look for a handle
            for node in idNodes:
                value = node.getText()
                if value.find("handle.net") != -1:
                    return value
            return "NONE"

        except Exception, e:
            self.log.error("Error fetching datastrem: ", e)
            self.throw_error("failure fetching datastrem: " + e.getMessage())
            return None

    # Parse and read an XML document
    def parse_xml(self, inputStrem):
        try:
            # First document in the list should run these
            if self.docFactory is None:
                self.docFactory = DocumentFactory()
            if self.saxReader is None:
                self.saxReader = SAXReader(self.docFactory)

            # The actual parsing
            reader = InputStreamReader(inputStrem, "UTF-8")
            return self.saxReader.read(reader);
        except Exception, e:
            self.log.error("Error parsing XML: ", e)
            self.throw_error("failure parsing XML: " + e.getMessage())
            return None

    # Connect to fedora and test access before returning
    def fedora_connect(self):
        # Read our configuration
        self.fedoraUrl = self.config.getString(None, ["transformerDefaults", "vital", "server", "url"])
        fedoraUsername = self.config.getString(None, ["transformerDefaults", "vital", "server", "username"])
        fedoraPassword = self.config.getString(None, ["transformerDefaults", "vital", "server", "password"])
        fedoraTimeout = self.config.getInteger(15, ["transformerDefaults", "vital", "server", "timeout"])
        if (self.fedoraUrl is None) or \
                (fedoraUsername is None) or (fedoraPassword is None):
            self.log.error("Invalid VITAL configuration!")
            self.throw_error("Invalid VITAL configuration!")
            return None

        # Establish and test the connection
        try:
            fedora = FedoraClient(self.fedoraUrl, fedoraUsername, fedoraPassword)
            fedora.SOCKET_TIMEOUT_SECONDS = fedoraTimeout
            return fedora
        except Exception, e:
            self.log.error("Error connecting to Fedora: ", e)
            self.throw_error("connecting to Fedora failed: " + e.getMessage())
            return None

    # Search solr for objects that have
    def search_solr(self):
        # Build our solr query
        vitalPidExists = "vitalPid:uon*"
        vitalHandleExists = "vitalHandle:http*"
        query = vitalPidExists + " AND NOT " + vitalHandleExists
        # Prepare the query
        req = SearchRequest(query)
        req.setParam("facet", "false")
        req.setParam("rows", "100")
        # Run the query
        try:
            out = ByteArrayOutputStream()
            self.services.getIndexer().search(req, out)
            return SolrResult(ByteArrayInputStream(out.toByteArray()))
        except Exception, e:
            self.log.error("Error searching solr: ", e)
            self.throw_error("failure searching solr: " + e.getMessage())
            return None

    def throw_error(self, message):
        self.vc["response"].setStatus(500)
        self.writer.println("Error: " + message)
        self.writer.close()
