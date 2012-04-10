
class FakeAndsDoiData:
    def __init__(self):
        pass

    def __activate__(self, context):
        self.velocityContext = context
        self.log = context["log"]

        response = self.vc("response")
        response.setStatus(200)
        self.writer = response.getPrintWriter("text/html; charset=UTF-8")
        self.writer.println("OK: DOI 10.5072/XX/XXXXXXXXXXX is successfully minted.")
        self.writer.close()

    # Get from velocity context
    def vc(self, index):
        if self.velocityContext[index] is not None:
            return self.velocityContext[index]
        else:
            log.error("ERROR: Requested context entry '" + index + "' doesn't exist")
            return None
