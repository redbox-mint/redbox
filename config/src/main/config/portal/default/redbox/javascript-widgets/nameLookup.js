var globalObject = this;

(function() {
    function getJson(queryUrl, timeoutSec, callback) {
        $.ajax({
            url: queryUrl,
            dataType: "json",
            timeout: timeoutSec * 1000,
            success: callback,
            error: function(x, s, e) {
                callback({
                    error: s
                });
            }
        });
    }

    var dialog, detailDialog;
    $(function() {
        dialog = $("<div>Test dialog message!</div>").dialog({
            title: "Name lookup",
            height: 450,
            maxHeight: 600,
            width: 450,
            modal: true,
            resizable: true,
            position: "center",
            draggable: true,
            autoOpen: false
        });
        detailDialog = $("<div/>").dialog({
            title: "Detail information",
            height: "auto",
            width: 400,
            modal: true,
            resizable: true,
            position: "center",
            draggable: true,
            autoOpen: false
        });
        gdialog = dialog;
    });

    var displayNameLookups = function(json, position, queryTerm, callback,
            getJson, nlaUrl, nlaFirstname, nlaSurname) {
        var mintDiv, nlaDiv, display;

        display = function() {
            var tbody, tr, td, label, id;
            mintDiv.html("");
            if (queryTerm) mintDiv.text("Search result for '" + queryTerm + "'");
            if (getJson) {
                var i, s;
                mintDiv.append("<br/>");
                i = $("<input type='text'/>");
                i.val(queryTerm);
                mintDiv.append(i);
                s = $("<input type='button' value='Search'/>");
                mintDiv.append(s);
                i.keypress(function(e) {
                    if (e.which == 13) s.click();
                });
                s.click(function() {
                    queryTerm = $.trim(i.val());
                    if (queryTerm) {
                        getJson(queryTerm, function(jdata) {
                            if (jdata.error) {
                                alert(jdata.error);
                            } else {
                                json = jdata;
                                display();
                                setTimeout(function() {
                                    try {
                                        i.focus();
                                    } catch(e) {
                                        // IE7?
                                    }
                                }, 10);
                            }
                        });
                    }
                });
            }
            mintDiv.append("<hr/>");
            mintDiv.append($("<table/>").append(tbody = $("<tbody/>")));
            $.each(json.results, function(c, result) {
                var r, a, name;
                id = "rId" + c;
                tr = $("<tr/>").append(td = $("<td/>"));
                r = $("<input type='radio' name='name' />").attr("id", id);
                r.val(JSON.stringify(result));
                label = $("<label/>").attr("for", id);
                name = result["rdfs:label"] || result["foaf:name"];
                label.append(name);
                if (result["dc:description"]) {
                    label.append(" - " + result["dc:description"]);
                }
                //
                td.append(r);
                td.append(label);
                //
                tr.append(td=$("<td/>"));
                a = $("<a style='color:blue;' href='#'>details</a>");
                td.append(a);
                tbody.append(tr);
                label.dblclick(function() {
                    dialog.dialog("option", "buttons").OK();
                });
                a.click(function(e) {
                    var pos = dialog.parent().position();
                    pos.left += 10;
                    pos.top += 20;
                    displayDetails(name, result, pos, r);
                    return false;
                });
            });

            // National Library Integration
            var nlaResultsDiv = $("<div/>");
            var nlaResultsProcess = function(data) {
                $(".nameLookup-waiting").hide();
                $(".nlaLookup-progress").hide();
                var searchMetadata = data.metadata;
                var pageStart = searchMetadata.startRecord-0;
                var pageRows = searchMetadata.rowsReturned-0;
                var pageTotal = searchMetadata.totalHits-0;
                var pageLast = (pageStart+pageRows-1);
                if (pageTotal == 0) {
                    pageStart = 0;
                }
                nlaResultsDiv.html("Showing "+pageStart+"-"+pageLast+" records of "+pageTotal+" total.");
                // Pagination
                var hasPrev = pageStart > 1;
                var hasNext = pageLast < pageTotal;
                var nlaPagination;
                if (hasPrev || hasNext) {
                    nlaResultsDiv.append(nlaPagination = $("<div/>"));
                }
                if (pageStart > 1) {
                    var prevLink = $("<a href='#'>&laquo; prev ("+pageRows+")</a>");
                    nlaPagination.append(prevLink);
                    if (hasNext) {
                        nlaPagination.append(" | ");
                    }
                    prevLink.click(function() {
                        var newStart = pageStart - pageRows;
                        if (newStart < 1) {
                            newStart = 1;
                        }
                        pagedNlaSearch(newStart, pageRows);
                    });
                }
                if (pageLast < pageTotal) {
                    var nextLink = $("<a href='#'>next ("+pageRows+") &raquo;</a>");
                    nlaPagination.append(nextLink);
                    nextLink.click(function() {
                        pagedNlaSearch(pageLast+1, pageRows);
                    });
                }

                nlaResultsDiv.append("<hr/>");
                nlaResultsDiv.append($("<table/>").append(tbody = $("<tbody/>")));
                $.each(data.results, function(c, result) {
                    var radio, detailLink, name;
                    // Radio input for each row
                    id = "rId" + c;
                    tr = $("<tr/>").append(td = $("<td/>"));
                    radio = $("<input type='radio' name='name' />").attr("id", id);
                    radio.val(JSON.stringify(result));
                    label = $("<label/>").attr("for", id);
                    name = result["displayName"];
                    label.append(name);
                    if (result["institution"]) {
                        label.append(" - " + result["institution"]);
                    }
                    td.append(radio);
                    td.append(label);

                    // Show more details
                    tr.append(td=$("<td/>"));
                    detailLink = $("<a style='color:blue;' href='#'>details</a>");
                    td.append(detailLink);
                    tbody.append(tr);
                    label.dblclick(function() {
                        dialog.dialog("option", "buttons").OK();
                    });
                    detailLink.click(function(e) {
                        var pos = dialog.parent().position();
                        pos.left += 10;
                        pos.top += 20;
                        displayDetails(name, result, pos, radio, true);
                        return false;
                    });
                });
            }
            var nlaResultsError = function(xhr, status, error) {
                $(".nameLookup-waiting").hide();
                $(".nlaLookup-progress").hide();
                nlaResultsDiv.html("ERROR: "+status);
            }
            function searchNla(start, rows) {
                var nlaQuery = "start="+start+"&rows="+rows;
                if (nlaSurname != null && nlaSurname != "") {
                    nlaQuery += "&surname=" + escape(nlaSurname) + "";
                }
                if (nlaFirstname != null && nlaFirstname != "") {
                    nlaQuery += "&firstName=" + escape(nlaFirstname) + "";
                }
                var url = nlaUrl.replace("{searchTerms}", escape(nlaQuery));
                $(".nameLookup-waiting").show();
                $(".nlaLookup-progress").show();
                nlaResultsDiv.html("");
                $.ajax({
                    url: url,
                    dataType: "json",
                    timeout: 15000,
                    success: nlaResultsProcess,
                    error: nlaResultsError
                });
            }

            // Search Form
            var nlaTbody, nlaTrow, nlaTcell;
            nlaDiv.append($("<table/>").append(nlaTbody = $("<tbody/>")));

            var nlaFirstnameInput = $("<input id='nlaFirstname' type='text' />");
            nlaFirstnameInput.val(nlaFirstname);
            nlaTbody.append(nlaTrow = $("<tr/>"));
            nlaTrow.append(nlaTcell = $("<td/>"));
            nlaTcell.append("<label for='nlaFirstname'>First Name:</label>");
            nlaTrow.append(nlaTcell = $("<td/>"));
            nlaTcell.append(nlaFirstnameInput);

            var nlaSurnameInput = $("<input id='nlaSurname' type='text' />");
            nlaSurnameInput.val(nlaSurname);
            nlaTbody.append(nlaTrow = $("<tr/>"));
            nlaTrow.append(nlaTcell = $("<td/>"));
            nlaTcell.append("<label for='nlaSurname'>Surname:</label>");
            nlaTrow.append(nlaTcell = $("<td/>"));
            nlaTcell.append(nlaSurnameInput);

            var nlaSearch = $("<input type='button' value='Search' />");
            nlaDiv.append(nlaSearch);
            nlaDiv.append("<hr/>");
            nlaDiv.append(nlaResultsDiv);
            nlaFirstnameInput.keypress(function(e) {
                if (e.which == 13) nlaSearch.click();
            });
            nlaSurnameInput.keypress(function(e) {
                if (e.which == 13) nlaSearch.click();
            });

            // Search metadata wrappers
            function pagedNlaSearch(start, rows) {
                nlaFirstname = $.trim(nlaFirstnameInput.val());
                nlaSurname = $.trim(nlaSurnameInput.val());
                searchNla(start, rows);
            }
            nlaSearch.click(function() {
                pagedNlaSearch(1, 10);
            });
            pagedNlaSearch(1, 10);
        };

        var loaderGif = $(".nameLookup-progress").html();
        var tabbedDiv = $("<div><ul><li><a href=\"#mintLookupDialog\">Mint</a></li><li><a href=\"#nlaLookupDialog\">NLA<span class=\"nlaLookup-progress\"> "+loaderGif+"</span></a></li></ul></div>");
        mintDiv = $("<div id=\"mintLookupDialog\"></div>");
        nlaDiv = $("<div id=\"nlaLookupDialog\"><div class='nameLookup-waiting'>Searching National Library. Please wait... "+loaderGif+"</div></div>");
        tabbedDiv.append(mintDiv);
        tabbedDiv.append(nlaDiv);

        display();
        dialog.html(tabbedDiv);
        tabbedDiv.tabs();

        dialog.dialog("option", "buttons", {
            "OK": function() {
                var value = mintDiv.find("input[name=name]:checked").val();
                if (value == null || value == "") {
                    value = nlaDiv.find("input[name=name]:checked").val();
                }
                dialog.dialog("close");
                detailDialog.dialog("close");
                if (value) {
                    callback(true, JSON.parse(value));
                } else {
                    callback(false);
                }
            },
            "Clear": function() {
                dialog.dialog("close");
                detailDialog.dialog("close");
                callback(false, "clear");
            },
            "Cancel": function() {
                dialog.dialog("close");
                detailDialog.dialog("close");
                callback(false);
            }
        });
        dialog.dialog("open");
    }

    var displayDetails = function(name, details, pos, link, nla) {
        var data, table;
        if (nla !== true) {
            nla = false;
        }

        // National Library
        if (nla === true) {
            detailDialog.html("Known identities for:");
            detailDialog.append("<h3>"+name+"</h3>");
            detailDialog.append("NLA Link: <a href=\""+details["nlaId"]+"\" target=\"_blank\">"+details["nlaId"]+"</a>");
            detailDialog.append("<hr/>");
            data = details["knownIdentities"];
            if (data) {
                table = $("<table/>");
                var length = data.length;
                for (var i = 0; i < length; i++) {
                    var row = data[i];
                    table.append($("<tr><th>Name</th><td>" + row["displayName"] + "</td></tr>"));
                    table.append($("<tr><th>Institution</th><td>" + row["institution"] + "</td></tr>"));
                    table.append($("<tr><td colspan=\"2\">&nbsp;</td></tr>"));
                }
                detailDialog.append(table);

            } else {
                $.each(details, function(k, v) {
                    var d = $("<div/>");
                    d.text(k + " : " + JSON.stringify(v));
                    detailDialog.append(d);
                });
            }

        // Mint
        } else {
            detailDialog.html("Details for:");
            detailDialog.append("<h3>"+name+"</h3>");
            data = details["result-metadata"]["all"];
            if (data) {
                table = $("<table/>");
                function addField(term,field) {
                    field = field || term;
                    table.append($("<tr ><th>" + term + "</th><td>" + data[field] + "</td></tr>"));
                }
                addField("Title", "Honorific");
                addField("Given_Name");
                addField("Family_Name");
                addField("Email");
                addField("Description");
                detailDialog.append(table);

            } else {
                $.each(details, function(k, v) {
                    var d = $("<div/>");
                    d.text(k + " : " + JSON.stringify(v));
                    detailDialog.append(d);
                });
            }
        }

        detailDialog.dialog("option", "buttons", {
            "OK": function(){
                link.click();
                detailDialog.dialog("close");
            },
            "Cancel": function(){
                detailDialog.dialog("close");
            }
        });
        detailDialog.dialog("open").dialog("moveToTop");
        detailDialog.parent().css("top", pos.top + "px").css("left", pos.left + "px");
    };

    function init() {
        $(".nameLookup-section").each(function(c, e) {
            nameLookupSection($(e));
        });
    }

    function nameLookupSection(ctx) {
        var url = ctx.find(".nameLookup-url").val();
        var nlaUrl = ctx.find(".nlaLookup-url").val();
        var valueNs = ctx.find(".nameLookup-value-ns").val();
        var textNs = ctx.find(".nameLookup-text-ns").val();
        function debug(msg) {
            ctx.find(".nameLookup-debugMsg").text(msg.toString());
        }
        //ctx.find(".nameLookup-lookup").unbind().click(function(e){
        ctx.find(".nameLookup-lookup").die().live("click", function(e) {
            var target, parent, queryTerm, queryUrl, cGetJson
            var selectedNameCallback;
            target = $(e.target);
            _gtarget = target;
            parent = target;
            while (parent.size() && (parent.find(".nameLookup-name").size() == 0)) {
                parent = parent.parent();
            }
            var progressElem = parent.find(".nameLookup-progress");
            queryTerm = parent.find(".nameLookup-name").map(function(i, e) {
                return e.value;
            });
            queryTerm = $.trim($.makeArray(queryTerm).join(" "));

            // Get our NLA URL values whilst here
            var nlaSurname = parent.find(".familyName").val();
            var nlaFirstname = parent.find(".givenName").val();

            // Note: double escape the parameter because it is being passed as a parameter inside a parameter
            progressElem.show();
            target.hide();
            selectedNameCallback = function(ok, result) {
                debug(ok);
                if (ok) {
                    // National Library of Australia
                    var nlaId = result["nlaId"];
                    if (nlaId != null) {
                        parent.find(".nlLabel").val(result["displayName"]);
                        parent.find(".nlId").val(nlaId);

                    // Mint Identity
                    } else {
                        function xUpdate(ns, what) {
                            var nsp, k;
                            if (!ns) return;
                            nsp = ns + "-";
                            parent.find("." + ns).each(function(c, e) {
                                e = $(e);
                                $.each(e.attr("class").split(/\s+/), function(_, cls) {
                                    if (cls.substr(0, nsp.length) === nsp) {
                                        k = cls.substr(nsp.length);
                                        if (result[k]) {
                                            e[what](result[k]);
                                        }
                                    }
                                });
                            });
                        }
                        xUpdate(valueNs, "val");
                        xUpdate(textNs, "text");
                    }

                    var selectedFunc = globalObject[target.dataset("selected-func")];
                    if ($.isFunction(selectedFunc)) {
                        try {
                            selectedFunc(target, result);
                        } catch(e) {
                            alert("Error executing selected-func. " + e.message);
                        }
                    }
                } else if (result == "clear") {
                    var clearedFunc = globalObject[target.dataset("cleared-func")];
                    if ($.isFunction(clearedFunc)) {
                        try {
                            clearedFunc(target, result);
                        } catch(e) {
                            alert("Error executing cleared-func. " + e.message);
                        }
                    }
                }
                progressElem.hide();
                target.show();
            };
            // curry getJson
            cGetJson = function(queryTerm, callback) {
                queryUrl = url.replace("{searchTerms}", escape(escape(queryTerm)));
                debug("clicked queryUrl=" + queryUrl);
                getJson(queryUrl, 6, callback);
            };
            cGetJson(queryTerm, function(json) {
                if (json.error) {
                    alert(json.error);
                } else {
                    //alert(json.results.length);
                    var position = target.position();
                    displayNameLookups(json, position, queryTerm,
                        selectedNameCallback, cGetJson, nlaUrl, nlaFirstname, nlaSurname);
                }
            });
            return false;
        });
        debug("loaded ok");
    }

    $(function() {
        init();
    });

    nameLookup = {
        init: init
    };
})($);
