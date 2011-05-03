class StageData:
    def __activate__(self, context):
        formData = context["formData"]
        sessionState = context["sessionState"]

        stageLabel = formData.get("stage")
        sessionState.set("fq", 'workflow_step_label:"%s"' % stageLabel)
        sessionState.set("SearchTitle", stageLabel)

        context["response"].sendRedirect("%s/search" % context["portalPath"])
