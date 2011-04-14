
class ResultData:
    def __activate__(self, context):
        self.services = context["Services"]
        self.page = context["page"]
        self.portalId = context["portalId"]
        self.metadata = context["metadata"]

    def canManage(self):
        workflowRoles = self.metadata.get("workflow_security")
        if workflowRoles:
            userRoles = self.page.authentication.get_roles_list()
            for role in userRoles:
                if role in workflowRoles:
                    return True
        return False

    def get(self, name):
        valueList = self.metadata.getList(name)
        if valueList.size() > 0:
            return valueList.get(0)
        return ""

    def getList(self, name):
        return self.metadata.getList(name)

    def getMimeTypeIcon(self, path, format, altText = None):
        if format[-1:] == ".":
            format = format[0:-1]
        if altText is None:
            altText = format
        # check for specific icon
        iconPath = "images/icons/mimetype/%s/icon.png" % format
        resource = self.services.getPageService().resourceExists(self.portalId, iconPath)
        if resource is not None:
            return "<img src=\"%s/%s\" title=\"%s\" alt=\"%s\" />" % (path, iconPath, altText, altText)
        elif format.find("/") != -1:
            # check for major type
            return self.getMimeTypeIcon(path, format.split("/")[0], altText)
        # use default icon
        iconPath = "images/icons/mimetype/icon.png"
        return "<img src=\"%s/%s\" title=\"%s\" alt=\"%s\" />" % (path, iconPath, altText, altText)


from org.apache.commons.lang import StringEscapeUtils

class ResultData:
    def __activate__(self, context):
        self.services = context["Services"]
        self.page = context["page"]
        self.portalId = context["portalId"]
        self.metadata = context["metadata"]

    def canManage(self):
        workflowRoles = self.metadata.get("workflow_security")
        if workflowRoles:
            userRoles = self.page.authentication.get_roles_list()
            for role in userRoles:
                if role in workflowRoles:
                    return True
        return False

    def get(self, name):
        return self.metadata.get(name)

    def getFirst(self, name):
        return self.metadata.getFirst(name)

    def getList(self, name):
        return self.metadata.getList(name)

    def getMimeTypeIcon(self, path, format, altText = None):
        if format[-1:] == ".":
            format = format[0:-1]
        if altText is None:
            altText = format
        # check for specific icon
        iconPath = "images/icons/mimetype/%s/icon.png" % format
        resource = self.services.getPageService().resourceExists(self.portalId, iconPath)
        if resource is not None:
            return "<img src=\"%s/%s\" title=\"%s\" alt=\"%s\" />" % (path, iconPath, altText, altText)
        elif format.find("/") != -1:
            # check for major type
            return self.getMimeTypeIcon(path, format.split("/")[0], altText)
        # use default icon
        iconPath = "images/icons/mimetype/icon.png"
        return "<img src=\"%s/%s\" title=\"%s\" alt=\"%s\" />" % (path, iconPath, altText, altText)

    def getEscapeHtml(self, value):
        return StringEscapeUtils.escapeHtml(value)
