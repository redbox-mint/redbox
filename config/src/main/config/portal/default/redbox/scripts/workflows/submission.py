import time

class SubmissionData:
    def __activate__(self, context):
        pass

    def getSubmitDate(self):
        return time.strftime("%Y-%m-%d")

