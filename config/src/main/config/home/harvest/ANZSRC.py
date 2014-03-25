import time
from org.semanticdesktop.aperture.rdf.impl import RDFContainerImpl
from com.googlecode.fascinator.vocabulary import SKOS
from com.googlecode.fascinator.vocabulary import DCTERMS
from org.ontoware.rdf2go.model.node import Variable
from org.ontoware.rdf2go.model.node.impl import URIImpl

class IndexData:
    def __init__(self):
        pass

    def __activate__(self, context):
        # Prepare variables
        self.index = context["fields"]
        self.object = context["object"]
        self.payload = context["payload"]
        self.params = context["params"]
        self.utils = context["pyUtils"]

        # Common data
        self.__newDoc()

        # Real metadata
        if self.itemType == "object":
            #self.__previews()
            self.__basicData()
            self.__metadata()

        # Make sure security comes after workflows
        self.__security()

    def __newDoc(self):
        self.oid = self.object.getId()
        self.pid = self.payload.getId()
        metadataPid = self.params.getProperty("metaPid", "DC")

        if self.pid == metadataPid:
            self.itemType = "object"
        else:
            self.oid += "/" + self.pid
            self.itemType = "datastream"
            self.utils.add(self.index, "identifier", self.pid)

        self.utils.add(self.index, "id", self.oid)
        self.utils.add(self.index, "storage_id", self.oid)
        self.utils.add(self.index, "item_type", self.itemType)
        self.utils.add(self.index, "last_modified", time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        self.utils.add(self.index, "harvest_config", self.params.getProperty("jsonConfigOid"))
        self.utils.add(self.index, "harvest_rules",  self.params.getProperty("rulesOid"))
        self.utils.add(self.index, "display_type", "skos")

    def __basicData(self):
        self.utils.add(self.index, "repository_name", self.params["repository.name"])
        self.utils.add(self.index, "repository_type", self.params["repository.type"])

    def __indexList(self, name, values):
        for value in values:
            print "indexing: '%s', value: '%s'" % (name, value)
            self.utils.add(self.index, name, value)

    def __security(self):
        roles = self.utils.getRolesWithAccess(self.oid)
        if roles is not None:
            for role in roles:
                self.utils.add(self.index, "security_filter", role)
        else:
            # Default to guest access if Null object returned
            schema = self.utils.getAccessSchema("derby");
            schema.setRecordId(self.oid)
            schema.set("role", "guest")
            self.utils.setAccessSchema(schema, "derby")
            self.utils.add(self.index, "security_filter", "guest")

    def __metadata(self):
        self.utils.registerNamespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.utils.registerNamespace("j.0", "http://www.w3.org/2004/02/skos/core#")
        self.utils.registerNamespace("dc", "http://purl.org/dc/terms/")
        self.utils.registerNamespace("foaf", "http://xmlns.com/foaf/0.1/")
        self.utils.registerNamespace("xsd", "http://www.w3.org/2001/XMLSchema#")
        self.utils.registerNamespace("rdfs", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.utils.registerNamespace("skos", "http://www.w3.org/2004/02/skos/core#")

        rdfAbout = URIImpl(self.params.getProperty("concept-uri"))
        self.utils.add(self.index, "dc_identifier", rdfAbout.toString())
        rdfPayload = self.object.getPayload(self.object.getSourceId())
        rdfModel = self.utils.getRdfModel(rdfPayload.open())
        rdfPayload.close()
        
        #index broader
        self.__indexPath("broader", self.params.getProperty("skos-uri"))

        #process dc title
        title = self.__getSingleValueFromCollection(rdfModel, rdfAbout, DCTERMS.title, Variable.ANY)

        if title == "":
           title = self.__getSingleValueFromCollection(rdfModel, rdfAbout, SKOS.prefLabel, Variable.ANY)
           #print "*** title2: ", title
        self.utils.add(self.index, "dc_title", title)

        #process the rest
        collection = rdfModel.findStatements(rdfAbout, Variable.ANY, Variable.ANY)
        while collection.hasNext():
            s = collection.next()
            value = s.getObject()
            if type(value).__name__=="URIImpl":
                value = value.toString()
            else:
                value = value.getValue()
            conceptUri = s.getPredicate().toString()
            #Can't use the NS_DCTERMS, so for now is hardcoded... dcNs = DCTERMS.NS_DCTERMS
            dcNs = "http://purl.org/dc/terms/"
            if conceptUri.startswith(dcNs):
                concept = conceptUri.split(dcNs)[1]
                if concept != "title":
                    self.utils.add(self.index, "dc_%s" % concept, value)

            skosNs = "http://www.w3.org/2004/02/skos/core#"
            if conceptUri.startswith(skosNs):
                concept = conceptUri.split(skosNs)[1]
                self.utils.add(self.index, "skos_%s" % concept, value)

            rdfNs = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            if conceptUri.startswith(rdfNs):
                concept = conceptUri.split(rdfNs)[1]
                self.utils.add(self.index, "rdf_%s" % concept, value)

    def __getSingleValueFromCollection(self, rdfModel, subjectURI, predicateURI, objURI):
        collection = rdfModel.findStatements(subjectURI, predicateURI, objURI)
        value = ""
        try:
            while collection.hasNext():
                s = collection.next()
                obj = s.getObject()
                if type(obj).__name__=="URIImpl":
                    value = obj.toString()
                else:
                    value = obj.getValue()
        except Exception, e:
            print " ** Error: ", str(e)
        return value

    def __getValueUsingFindStatement(self, rdfModel, subject, preUri, objUri, getSubject=True):
        iterator = rdfModel.findStatements(subject, preUri, objUri)
        subjectVal = ""
        objectVal = ""
        while iterator.hasNext():
            statement = iterator.next()
            subjectVal = statement.getSubject().toString()
            objectVal = statement.getObject().toString()
        if getSubject:
            return subjectVal
        return objectVal



    def __indexPath(self, name, path, includeLastPart=True):
        path = path.encode("utf8").rstrip("/")
        parts = path.split("/")
        length = len(parts)
        if includeLastPart:
            length +=1
        for i in range(1, length):
            part = "/".join(parts[:i])
            if part != "":
                if part.startswith("/"):
                    part = part[1:]
                self.utils.add(self.index, name, part)
