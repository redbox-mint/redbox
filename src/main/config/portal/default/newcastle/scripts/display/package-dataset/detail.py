from org.apache.commons.lang import StringEscapeUtils
from org.apache.commons.io import IOUtils
from java.io import StringWriter
from java.util import LinkedHashMap

class DetailData:
    def __init__(self):
        pass

    def __activate__(self, context):
        self.page = context["page"]
        self.metadata = context["metadata"]
        self.Services = context.get("Services")
        self.formData = context.get("formData")

    def hasWorkflow(self):
        self.__workflowStep = self.metadata.getList("workflow_step_label")
        if self.__workflowStep.isEmpty():
            return False
        return True

    def hasWorkflowAccess(self):
        userRoles = self.page.authentication.get_roles_list()
        workflowSecurity = self.metadata.getList("workflow_security")
        for userRole in userRoles:
            if userRole in workflowSecurity:
                return True
        return False

    def getWorkflowStep(self):
        return self.__workflowStep[0]

    def getJsonMetadata(self, oid):
        # get the TF package manifest
        object = self.Services.storage.getObject(oid)
        sourceId = object.getSourceId()
        payload = object.getPayload(sourceId)
        writer = StringWriter()
        IOUtils.copy(payload.open(), writer)
        json = writer.toString()
        payload.close()
        return json

    def getList(self, baseKey):
        if baseKey[-1:] != ".":
            baseKey = baseKey + "."
        valueMap = LinkedHashMap()
        metadata = self.metadata.getJsonObject()
        for key in [k for k in metadata.keySet() if k.startswith(baseKey)]:
            value = metadata.get(key)
            field = key[len(baseKey):]
            index = field[:field.find(".")]
            #print "%s. '%s' = '%s'" % (index, key, value)
            data = valueMap.get(index)
            if not data:
                data = LinkedHashMap()
                valueMap.put(index, data)
            if len(value) == 1:
                value = value.get(0)
            data.put(field[field.find(".")+1:], value)
        return valueMap

    def escape(self, value):
        return StringEscapeUtils.escapeHtml(value)

    def test(self):
        return "-test() scripts/display/default/detail.py-"

