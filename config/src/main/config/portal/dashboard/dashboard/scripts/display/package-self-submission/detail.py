from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.api.storage import StorageException
from com.googlecode.fascinator.common import JsonObject, JsonSimple
from java.io import ByteArrayInputStream, ByteArrayOutputStream, File
from java.lang import Exception, System, String
from java.util import TreeMap, TreeSet, ArrayList, HashMap
from com.googlecode.fascinator.portal.lookup import MintLookupHelper

from org.apache.commons.lang import StringEscapeUtils, WordUtils
from org.json.simple import JSONArray

class DetailData:
    def __init__(self):
        pass

    def __activate__(self, context):
        self.page = context["page"]
        self.metadata = context["metadata"]
        self.log = context["log"]
        self.systemConfig = context["systemConfig"]
    
    # get a list of metadata using basekey. Used by repeatable elements like FOR code or people
    def getList(self, baseKey):
        if baseKey[-1:] != ".":
            baseKey = baseKey + "."
        valueMap = TreeMap()
        metadata = self.metadata.getJsonObject()
        for key in [k for k in metadata.keySet() if k.startswith(baseKey)]:
            value = metadata.get(key)
            field = key[len(baseKey):]
            index = field[:field.find(".")]
            if index == "":
                valueMapIndex = field[:key.rfind(".")]
                dataIndex = "value"
            else:
                valueMapIndex = index
                dataIndex = field[field.find(".")+1:]
            #print "%s. '%s'='%s' ('%s','%s')" % (index, key, value, valueMapIndex, dataIndex)
            data = valueMap.get(valueMapIndex)
            #print "**** ", data
            if not data:
                data = TreeMap()
                valueMap.put(valueMapIndex, data)
            if len(value) == 1:
                value = value.get(0)
            data.put(dataIndex, value)
        return valueMap
    
    # ability to add to pull the dropdown label off a json file using the value
    # Two formats are supported through the same two-argument interface
    def getLabel(self, jsonFile, key):
        value = self.metadata.get(key)
        jsonLabelFile = System.getProperty("fascinator.home") + jsonFile
        jsonF = JsonSimple(File(jsonLabelFile))
        entries = jsonF.getJsonArray()
        if entries is None:
            entries = jsonF.getArray('results')
            if entries is None:
                self.log.debug("Unknown data source format: JSON file {} or its 'results' has no array.", jsonLabelFile)
                return None
        
        for entry in entries:
            entryJson = JsonSimple(entry)
            if value == entryJson.getString("", "id"):
                return entryJson.getString("", "label")
            elif value == entryJson.getString("", "value"):
                return entryJson.getString("", "label")
            
        return None
  
    # method for looking up Mint labels
    def getMintLabels(self, urlName, key, suffix):
        mapIds = HashMap()
        valList = self.getList(key)
        ids = ""
        for eKey in valList.keySet():
            entry = valList.get(eKey)
            if len(ids) > 0: 
               ids = "%s,"%ids            
            ids = "%s%s" % (ids,entry.get(suffix))
        if ids == "":
            return None
        else:           
            labels = ArrayList()
            mapIds.put("id", ids) 
            labelsMint = MintLookupHelper.get(self.systemConfig, urlName, mapIds)            
            self.log.debug(labelsMint.getJsonArray().toString())    
            for label in labelsMint.getJsonArray():
                 labelJson = JsonSimple(label)
                 labels.add(labelJson.getString("", "label"))
            return labels
        
    def getMintLabelByLookup(self, urlName, key, resKey, valKey):
        rawValue = self.metadata.get(key)                    
        if not hasattr(rawValue, 'strip'):
            return None
        
        mapIds = HashMap()
        value = String().replace(":", "\:")
        if value is None:
            return None
        labels = ArrayList()        
        mapIds.put("searchTerms", value) 
        labelsMint = MintLookupHelper.get(self.systemConfig, urlName, mapIds)            
        self.log.debug(labelsMint.toString())
        resultsArr = labelsMint.getArray(resKey)        
        if resultsArr is None:
            return None
        for result in resultsArr:
            labelJson = JsonSimple(result)
            labels.add(labelJson.getString("", valKey))            
        return labels