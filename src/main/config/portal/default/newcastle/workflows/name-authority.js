$(function() {
    $("#update-package").click(function() {
        $.post("$portalPath/actions/manifest.ajax",
            {   func: "update-package-meta",
                oid: "$oid",
                metaList: ["title", "description"],
                title: $("#package-title").val(),
                description: $("#package-description").val()
            },
            function(data, status) {
                $("#package-form").submit();
            });
        return false;
    });
});
