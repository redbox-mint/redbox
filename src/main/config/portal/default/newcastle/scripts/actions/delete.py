from java.lang import Exception

class DeleteData:
    def __init__(self):
        pass

    def __activate__(self, context):
        self.vc = context
        self.writer = self.vc["response"].getPrintWriter("text/html; charset=UTF-8")
        self.auth = self.vc["page"]
        self.process()
        #self.throw_error("Only administrative users can access this feature")

    def process(self):
        record = self.vc["formData"].get("record")
        try:
            Services.storage.removeObject(record)
            Services.indexer.remove(record)
            Services.indexer.annotateRemove(record)
            self.writer.println(record)
            self.writer.close()
        except Exception, e:
            self.throw_error("Error deleting object: " + e.getMessage())

    def throw_error(self, message):
        self.vc["response"].setStatus(500)
        self.writer.println("Error: " + message)
        self.writer.close()
