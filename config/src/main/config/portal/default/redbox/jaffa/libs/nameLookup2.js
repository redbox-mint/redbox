function replaceDots(id) {
	return id.replace(/./g,'\\.');
}

//Called from anywhere where needs name lookup
//title is not used in search
function showMintNlaLookupDialog(e, lookup_source) {
	var input_sibs = $(e).parent().find('input');
	var ids = new Array();
    for (i = 0; i < input_sibs.length; i++) {
        if (input_sibs[i].type == 'text' || input_sibs[i].type == 'hidden') {
            ids.push(input_sibs[i].id);
        }
    }
	NameLookUp(ids, lookup_source.split(','))
}

function NameLookUp(ids, lookup_source) {
	var queryTerm = document.getElementById(ids[1]).value;
	for (var i = 2; i< ids.length-1; i++) { // skip the last hidden field: dcIdentifier
		queryTerm += " " + document.getElementById(ids[i]).value;
	}
	queryTerm = queryTerm.trim();

	var mintUrl = $(".nameLookup-url").val();
	var nlaUrl = $(".nlaLookup-url").val();

	var loaderGif = $("<span class=\"nameLookup-progress hidden\"><img src=\"/redbox/default/images/icons/loading.gif\"></span>").html();
	var mintDiv = $("<div id=\"mintLookupDialog\"></div>");
	var nlaDiv = $("<div id=\"nlaLookupDialog\"><div class='nameLookup-waiting'>Searching National Library. Please wait... "+loaderGif+"</div></div>");
	var tabbedDiv = $("<div><ul><li><a href=\"#mintLookupDialog\">Mint</a></li><li><a href=\"#nlaLookupDialog\">NLA<span class=\"nlaLookup-progress\"> "+loaderGif+"</span></a></li></ul></div>");
	
	var dlgMint, detailDialog;
	dlgMint = $("<div>Mint lookup dialog place holder</div>").dialog({
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

	dlgMint.dialog("option", "buttons", {
		"OK": function() {
			var value = mintDiv.find("input[name=name]:checked").val();
			if (value == null || value == "") {
				value = nlaDiv.find("input[name=name]:checked").val();
			}
			dlgMint.dialog("close");
			detailDialog.dialog("close");
			if (value) {
				btn_callback(true, JSON.parse(value));
			} else {
				btn_callback(false);
			}
		},
		"Cancel": function() {
			dlgMint.dialog("close");
			detailDialog.dialog("close");
			btn_callback(false);
		}
	});

	var myTable; // For mint results
	var nlaFirstname, nlaSurname
	var nlaResultsDiv = $("<div/>");
	search_show();

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

//	ids[0]: title; ids[1]: firstName; ids[2]: surName; ids[3]: mintId
	function btn_callback(ok, result) {
		if (ok) {
			var selectedFunc = 'lookupDone';
			try {
				var nlaId = result["nlaId"];
				if (nlaId != null) {
					document.getElementById(ids[0]).value = "";
					$(document.getElementById(ids[0])).change();
					document.getElementById(ids[1]).value = result["firstName"];
					$(document.getElementById(ids[1])).change();
					document.getElementById(ids[2]).value = result["surname"];
					$(document.getElementById(ids[2])).change();
					// Mint Identity
				} else {
					// Mint Only
					var lookupData=result["result-metadata"].all;
					document.getElementById(ids[0]).value = lookupData["Honorific"];
					$(document.getElementById(ids[0])).change();
					document.getElementById(ids[1]).value = lookupData["Given_Name"];
					$(document.getElementById(ids[1])).change();
					document.getElementById(ids[2]).value = lookupData["Family_Name"];
					$(document.getElementById(ids[2])).change();
					document.getElementById(ids[3]).value = lookupData["Email"];
					$(document.getElementById(ids[3])).change();
					document.getElementById(ids[4]).value = lookupData["dc_identifier"];
					$(document.getElementById(ids[4])).change();
				}
			} catch(e) {
				alert("Error executing selected-func. " + e.message);
			}
		}
	};

	function makeWnd(queryTerm) {
//		tab view
//		tabbedDiv.append(mintDiv);
//		tabbedDiv.append(nlaDiv);
//
//		dlgMint.html(tabbedDiv);
//		tabbedDiv.tabs();
		if(lookup_source.length == 1) {
		if (lookup_source.indexOf('mint') != -1) {
			dlgMint.html(mintDiv);
		} else {
			dlgMint.html(nlaDiv);
		}
		} else {
			tabbedDiv.append(mintDiv);
			tabbedDiv.append(nlaDiv);
			dlgMint.html(tabbedDiv);
			tabbedDiv.tabs();
		}
		
		var tbody, tr, td, label, id;
		mintDiv.html("");
		if (queryTerm) mintDiv.text("Search result for '" + queryTerm + "'");

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
				getJson(constructQueryUrl(queryTerm), 6, function(jdata) {
					if (jdata.error) {
						alert(jdata.error);
					} else {
						json = jdata;
						updateTable(json);
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
		mintDiv.append("<hr/>");
		mintDiv.append(myTable = $("<table id=\"mintResult\"/>"));
		myTable.html($("<tr><td>No results</td></tr>"));
	}

	function updateTable(searchResults) {
		var tr;
		myTable.html("");
		$.each(searchResults.results, function(c, result) {
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
			myTable.append(tr);
			label.dblclick(function() {
				dlgMint.dialog("option", "buttons").OK();
			});
			a.click(function(e) {
				var pos = dlgMint.parent().position();
				pos.left += 10;
				pos.top += 20;
				displayDetails(name, result, pos, r);
				return false;
			});
		});
	}

	function displayNLA(data) {
		// National Library Integration
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
		// Construct Search Form
		var nlaTbody, nlaTrow, nlaTcell;
		nlaResultsDiv.append($("<table/>").append(nlaTbody = $("<tbody/>")));

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

		nlaFirstnameInput.keypress(function(e) {
			if (e.which == 13) nlaSearch.click();
		});
		nlaSurnameInput.keypress(function(e) {
			if (e.which == 13) nlaSearch.click();
		});

		var nlaSearch = $("<input type='button' value='Search' />");
		nlaSearch.click(function() {
			pagedNlaSearch(1, 10);
		});
		nlaResultsDiv.append(nlaSearch);
		nlaResultsDiv.append("<hr/>");

		nlaResultsDiv.append($("<p>Showing "+pageStart+"-"+pageLast+" records of "+pageTotal+" total.</p>"));
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
				dlgMint.dialog("option", "buttons").OK();
			});
			detailLink.click(function(e) {
				var pos = dlgMint.parent().position();
				pos.left += 10;
				pos.top += 20;
				displayDetails(name, result, pos, radio, true);
				return false;
			});
		});
		nlaDiv.append(nlaResultsDiv);
		// Search metadata wrappers
		function pagedNlaSearch(start, rows) {
			nlaFirstname = $.trim(nlaFirstnameInput.val());
			nlaSurname = $.trim(nlaSurnameInput.val());
			searchNla(start, rows);
		}

	}

	var nlaResultsError = function(xhr, status, error) {
		$(".nameLookup-waiting").hide();
		$(".nlaLookup-progress").hide();
		nlaResultsDiv.html("ERROR: "+status);
	}

	function searchNla(start, rows) {
		if (lookup_source.indexOf('nla') == -1) { return; }
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
			success: displayNLA,
			error: nlaResultsError
		});
	}

	function constructQueryUrl(queryTerm) {
		return mintUrl.replace("{searchTerms}", escape(escape(queryTerm)));
	}

	function displayDetails(name, details, pos, link, nla) {
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
	}

	function search_show() {
		makeWnd(queryTerm);
		if (lookup_source.indexOf('mint') !=-1) { 
			getJson(constructQueryUrl(queryTerm), 6, function(json) {
				if (json.error) {
					alert(json.error);
				} else {
					updateTable(json);
				}});
		}
		if (lookup_source.indexOf('nla') !=-1) {
			searchNla(1, 10);
		}
		if(lookup_source.length > 1) {
			dlgMint.find('[href=#mintLookupDialog]')[0].click();
		}
		dlgMint.dialog('open'); 
	}
};
