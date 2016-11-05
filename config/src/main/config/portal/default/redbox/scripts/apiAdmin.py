from com.googlecode.fascinator.common import JsonSimple, JsonObject
from com.googlecode.fascinator.common import FascinatorHome
from org.json.simple import JSONArray
from org.apache.commons.io import FileUtils
from java.util import UUID


class ApiAdminData:

    def __init__(self):
        pass

    def __activate__(self, context):
        self.velocityContext = context
        self.formData = self.velocityContext["formData"]
        self.request = self.velocityContext["request"]
        if self.request.getMethod() == "POST":
            if self.formData.get("action") == "Add":
                self.add_key()
            if self.formData.get("action") == "Remove":
                self.remove_key()
            if self.formData.get("action") == "Regenerate":
                self.regenerate_key()
        self.json = JsonSimple()

    def parse_json(self, json_string):
        self.json = JsonSimple(json_string)

    def regenerate_key(self):
        keysFile = FascinatorHome.getPathFile("security/apikeys.json")
        keysJsonSimple = JsonSimple(keysFile)
        clientArray = keysJsonSimple.getArray("api", "clients")
        name = self.formData.get("name")
        clientToBeReplaced = None
        index = 0
        for client in clientArray:
            if client.get("name") == name:
                clientToBeReplaced = client
                break
            index = index + 1

        if clientToBeReplaced is not None:
            clientObject = JsonObject()
            clientObject.put("name", self.formData.get("name"))
            clientObject.put("key", self.get_random_key())
            clientArray.set(index,clientObject)
            FileUtils.writeStringToFile(keysFile, keysJsonSimple.toString(True))

    def remove_key(self):
        keysFile = FascinatorHome.getPathFile("security/apikeys.json")
        keysJsonSimple = JsonSimple(keysFile)
        clientArray = keysJsonSimple.getArray("api", "clients")
        name = self.formData.get("name")
        clientToBeRemoved = None
        for client in clientArray:
            if client.get("name") == name:
                clientToBeRemoved = client
                break
        if clientToBeRemoved is not None:
            clientArray.remove(clientToBeRemoved)
            FileUtils.writeStringToFile(keysFile, keysJsonSimple.toString(True))

    def add_key(self):
        keysFile = FascinatorHome.getPathFile("security/apikeys.json")
        keysJsonSimple = JsonSimple(keysFile)
        clientArray = keysJsonSimple.getArray("api", "clients")

        name = self.formData.get("name")
        for client in clientArray:
            if client.get("name") == name:
                return

        clientObject = JsonObject()
        clientObject.put("name", self.formData.get("name"))
        if(self.formData.get("generateKey") == "true"):
            clientObject.put("key", self.get_random_key())
        else:
            clientObject.put("key", self.formData.get("key"))
        clientArray.add(clientObject)
        FileUtils.writeStringToFile(keysFile, keysJsonSimple.toString(True))

    def get_random_key(self):
        return UUID.randomUUID().toString()
    def get_keys(self):
        keyJson = None
        keysFile = FascinatorHome.getPathFile("security/apikeys.json")
        if keysFile.exists():
            clientArray = JsonSimple(keysFile).getArray("api", "clients")
        else:
            clientArray = JSONArray()

        responseJson = JsonObject()
        responseJson.put("keys", clientArray)
        return responseJson
