class StageData:
    def __activate__(self, context):
        formData = context["formData"]
        sessionState = context["sessionState"]

        stageLabel = formData.get("stage")
        sessionState.set("fq", 'workflow_step_label:"%s"' % stageLabel)
        sessionState.set("SearchTitle", stageLabel)
        # Without a session variable storing our portalId, Fascinator will assume
        # this is a view swap and purge our cached filter before it ever runs.
        sessionState.set("lastPortalId", context["portalId"])

        context["response"].sendRedirect("%s/search" % context["portalPath"])
