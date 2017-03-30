from com.googlecode.fascinator.portal.services import OwaspSanitizer


class OwaspData:
    def __init__(self):
        pass

    def __activate__(self, context):
        self.log = context["log"]
        self.velocityContext = context
        self.writer = context["response"].getPrintWriter("application/json; charset=UTF-8")
        try:
            self.owaspSanitize(context["formData"].get("raw"))
        except:
            self.throw_error("Problem with sanitizing")
        finally:
            self.writer.close()

    def owaspSanitize(self, value):
        self.log.debug("sanitizing....")
        sanitized = OwaspSanitizer.sanitizeHtml(value)
        result = '{"response" : "%s"}' % sanitized
        self.writer.println(result)

    def throw_error(self, message):
        self.velocityContext["response"].setStatus(500)
        result = '{"response": "Error: %s"}' % message
        self.writer.println(result)
