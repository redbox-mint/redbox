from AlertException import AlertException
from AlertHandler import AlertHandler

from org.dom4j import DocumentFactory
from org.dom4j.io import SAXReader
from org.dom4j.xpath import DefaultNamespaceContext
from org.dom4j.xpath import DefaultXPath
from org.jaxen import SimpleNamespaceContext

from com.googlecode.fascinator.common import JsonObject
from com.googlecode.fascinator.common import JsonSimple

from org.json.simple import JSONArray

from java.io import File
from java.io import FileInputStream
from java.io import InputStreamReader
from java.lang import Exception
from org.apache.commons.lang.text import StrSubstitutor

import os

class XMLAlertHandler(AlertHandler):
    ''''Processing class for a single XML File.
    Each XML file is expected to contain only a single Collection
    '''

    def __init__(self, file, config, baseline):
        AlertHandler.__init__(self, file, config, baseline)
        docFactory = DocumentFactory()
        self.saxReader = SAXReader(docFactory)
        self.xmlMapFile = StrSubstitutor.replaceSystemProperties(config['xmlMap'])
        if not os.path.exists(self.xmlMapFile):
            raise AlertException("Requested xmlMap file %s does not exist." % self.xmlMapFile)
        
        ## Make sure we can see our mappings
        inStream = FileInputStream(File(self.xmlMapFile))
        xmlMappings = JsonSimple(inStream)
        self.map = xmlMappings.getObject(["mappings"])
        self.exceptions = xmlMappings.getObject(["exceptions"])
        self.defaultNamespace = xmlMappings.getString(None, ["defaultNamespace"])
        
        self.mappedExceptionCount = 0
        
        
    def process(self):
        '''Read the XML file and map xpath items to metadata
        Return a list with 1 JsonSimple object (at most)
        '''
        jsonList = []
        data = None
        reader = None
        inStream = None
        document = None
        
        # Run the XML through our parser
        try:
            inStream = FileInputStream(File(self.file))
            reader = InputStreamReader(inStream, "UTF-8")
            document = self.saxReader.read(reader)
        # Parse fails
        except:
            raise
        # Close our file access objects
        finally:
            if reader is not None:
                reader.close()
            if inStream is not None:
                inStream.close()

        # Now go looking for all our data
        data = self.getNewJsonObject()
        self.__mapXpathToFields(document, self.map, data)
        
        if data is None:
            return None
        
        jsonList.append(JsonSimple(data))
        return jsonList


    ## Used recursively
    def __mapXpathToFields(self, sourceData, map, responseData, index = 1):
        for xpath in map.keySet():
            field = map.get(xpath)
            if xpath != "":
                xpathobj = DefaultXPath(xpath)
                if not self.defaultNamespace is None:
                    xpathobj.setNamespaceContext(SimpleNamespaceContext(defaultNS))
                    
                nodes = xpathobj.selectNodes(sourceData)
                
                if isinstance(field, JsonObject):
                    #The XPath key provides a dictionary containing sub xpath queries mapped to fields
                    i = 1
                    for node in nodes:
                        self.__mapXpathToFields(node, field, responseData, i)
                        i += 1
                else:
                    # Lists indicate we're copying the several fields
                    if isinstance(field, JSONArray):
                        for eachField in field:
                            self.__insertFieldData(nodes, eachField, responseData, index)
                    # or just one field
                    else:
                        self.__insertFieldData(nodes, field, responseData, index)

    def __insertFieldData(self, xmlNodes, field, responseData, index):
        multiValue = False
        multiIndex = 1
        fieldString = ""
        
        if self.exceptions["fields"].containsKey(field):
            #The field is an exception
            excepted = True
            output = self.exceptions["output"]
            self.mappedExceptionCount += 1
        else:
            # Nope, just normal
            excepted = False
            if ('.0.' in field and len(xmlNodes) > 1): 
            #In ReDBox, a field such as dc:subject.vivo:keyword.0.rdf:PlainLiteral indicates a list of values, using the number as a counter.
            #In the code below, if a field contains this number element, we can increment the counter and add more and more. 
            #If there is no number, we just overwrite the value.
                multiValue = True
                #we'll do the fieldString index change a little later
                fieldString = field
            else:
                fieldString = field.replace(".0.", ".%s."%index, 1)
            
        for node in xmlNodes:
            text = node.getTextTrim()
                
            if fieldString != "" and text != "":
                if excepted:
                    exceptionString = "%s: '%s' (%s)" % (exceptions["fields"][field], text, field)
                    responseData.put(fieldString, exceptionString)
                else:
                    if multiValue:
                        fieldString = field.replace(".0.", ".%s."%multiIndex, 1)
                        multiIndex += 1
                    responseData.put(fieldString, text)
    