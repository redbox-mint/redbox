from com.googlecode.fascinator.common import JsonConfigHelper
from com.googlecode.fascinator.common import JsonObject
from com.googlecode.fascinator.common.messaging import MessagingServices
from com.googlecode.fascinator.messaging import TransactionManagerQueueConsumer

class VitalData:
    def __init__(self):
        self.messaging = MessagingServices.getInstance()

    def __activate__(self, context):
        self.auth = context["page"].authentication
        self.log = context["log"]
        self.log.info("Manual VITAL integration request received")

        response = context["response"]
        writer = response.getPrintWriter("text/plain; charset=UTF-8")

        result = JsonConfigHelper()
        result.set("status", "error")
        result.set("message", "An unknown error has occurred")

        if self.auth.is_logged_in() and self.auth.is_admin():
            self.log.info("VITAL: Valid administrative user")
            formData = context["formData"]
            func = formData.get("func")
            oid = formData.get("oid")
            if func == "refresh":
                if oid:
                    self.log.info("VITAL: Refresh event: '{}'", oid)
                    self.sendMessage(oid);
                    result.set("status", "ok")
                    result.set("message", "Object '%s' queued for refresh" % oid)
                else:
                    self.log.info("VITAL: No OID provided (500)")
                    response.setStatus(500)
                    result.set("message", "No object specified for refresh")
            else:
                self.log.info("VITAL: Unknown action '{}' (500)", func)
                response.setStatus(500)
                result.set("message", "Unknown action '%s'" % func)
        else:
            self.log.info("VITAL: Not an administrative user (500)")
            response.setStatus(500)
            result.set("message", "Only administrative users can access this API")
        writer.println(result.toString(True))
        writer.close()

    def sendMessage(self, oid):
        # Fake a workflow reindex. ReDBox doesn't need to reindex,
        #  the VITAL subscriber just needs to think we did.
        message = JsonObject()
        message.put("oid", oid)
        message.put("eventType", "ReIndex")
        message.put("username", self.auth.get_username())
        message.put("context", "Workflow")
        message.put("task", "workflow")
        self.messaging.queueMessage(
                TransactionManagerQueueConsumer.LISTENER_ID,
                message.toString())
