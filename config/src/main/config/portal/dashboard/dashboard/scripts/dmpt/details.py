class DetailsData:

    def __init__(self):
        pass
    
    def __activate__(self, context):
        self.request = context["request"]
        self.response = context["response"]
        self.formData = context["formData"]
        self.log = context["log"]
        oid = self.request.getParameter("oid")
        if oid is None:
            uri = self.request.getAttribute("RequestURI").split("/")
            oid = uri[len(uri)-1]
        self.response.sendRedirect(context["portalPath"] +"/detail/"+oid+"/")