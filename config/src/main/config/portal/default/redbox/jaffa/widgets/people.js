var PeopleWidgetBuilder = function($, jaffa) {
    var textClass = jaffa.widgets.baseWidget.extend({
        field: null,
        oldField: null,
        v2rules: {},

        deleteWidget: function() {
        	var titleFieldId= this.field+"foaf:title";
            var givenNameFieldId= this.field+"foaf:givenName";
            var familyNameFieldId= this.field+"foaf:familyName";
            var emailFieldId= this.field+"foaf:email";
            var dcIdentifierId = this.field+"dc:identifier";
            jaffa.form.ignoreField(titleFieldId);
            jaffa.form.ignoreField(givenNameFieldId);
            jaffa.form.ignoreField(familyNameFieldId);
            jaffa.form.ignoreField(emailFieldId);
            jaffa.form.ignoreField(dcIdentifierId);
            this.getContainer().remove();
        },
        // Identity has been altered, adjust the DOM for all fields
        domUpdate: function(from, to, depth) {
            this._super(from, to, depth);
            // Store, we'll need them to notify Jaffa later
            this.oldField = this.field;
            // Replace the portion of the ID that changed
            this.field = this.oldField.domUpdate(from, to, depth);
            // Update DOM but constrain searches to container, since there may
            //  be very temporary duplicate IDs as sort orders swap
            var container = this.getContainer();
            container.find("input[id=\""+this.oldField+".foaf:title\"]").attr("id", this.field+".foaf:title");
            container.find("input[id=\""+this.oldField+".foaf:givenName \"]").attr("id", this.field+".foaf:givenName");
            container.find("input[id=\""+this.oldField+".foaf:familyName\"]").attr("id", this.field+".foaf:familyName");
            container.find("input[id=\""+this.oldField+"dc:identifier\"]").attr("id", this.field+"dc:identifier");
            
            // Tell Jaffa to ignore the field's this widget used to manage
            var titleFieldId= this.oldField+"foaf:title";
            var givenNameFieldId= this.oldField+"foaf:givenName";
            var familyNameFieldId= this.oldField+"foaf:familyName";
            var emailFieldId= this.oldField+"foaf:email";
            var dcIdentifierId = this.oldField+"dc:identifier";
            jaffa.form.ignoreField(titleFieldId);
            jaffa.form.ignoreField(givenNameFieldId);
            jaffa.form.ignoreField(familyNameFieldId);
            jaffa.form.ignoreField(emailFieldId);
            jaffa.form.ignoreField(dcIdentifierId);
            
        },
        // Notify Jaffa that field <=> widget relations need to be updated
        //  This is called separately from above to avoid duplicate IDs that
        //   may occur whilst DOM alterations are occuring
        jaffaUpdate: function() {
            // Only synch if an update has effected this widget
            if (this.oldField != null) {
                this._super();
                var titleFieldId= this.field+"foaf:title";
            	var givenNameFieldId= this.field+"foaf:givenName";
            	var familyNameFieldId= this.field+"foaf:familyName";
            	var emailFieldId= this.field+"foaf:email";
            	var dcIdentifierId = this.field+"dc:identifier";
            	jaffa.form.addField(titleFieldId, this.id());
            	jaffa.form.addField(givenNameFieldId, this.id());
            	jaffa.form.addField(familyNameFieldId, this.id());
            	jaffa.form.addField(emailFieldId, this.id());
            	jaffa.form.addField(dcIdentifierId, this.id());
                this.oldField = null;
            }
            // TODO: Validation alterations ?? Doesn't seem to matter
        },

        // Whereas init() is the constructor, this method is called after Jaffa
        // knows about us and needs us to build UI elements and modify the form.
        buildUi: function() {
            var ui = this.getContainer();
            ui.html("");

            // Field
            this.field = this.getConfig("field");
            if (this.field == null) {
                // TODO: Testing
                jaffa.logError("No field name provided for widget '"+this.id()+"'. This is mandatory!");
                return;
            }
            if(this.field.indexOf(".", this.field.length - 1) == -1) {
            	this.field = this.field+".";
            }
            
            var lookup_only = this.getConfig("lookup-only");
            var titleFieldId= this.field+"foaf:title";
            ui.append("<label for=\""+titleFieldId+"\" class=\"widgetLabel peopleWidgetLabel\">Title</label>");
            ui.append("<input type=\"text\" id=\""+titleFieldId+"\" class=\"jaffa-field\" />");
            
            var givenNameFieldId= this.field+"foaf:givenName";
            ui.append("<label for=\""+givenNameFieldId+"\" class=\"widgetLabel peopleWidgetLabel\">Given Name</label>");
            ui.append("<input type=\"text\" id=\""+givenNameFieldId+"\" class=\"jaffa-field\" />");
            
            var familyNameFieldId= this.field+"foaf:familyName";
            ui.append("<label for=\""+familyNameFieldId+"\" class=\"widgetLabel peopleWidgetLabel\">Family Name</label>");
            ui.append("<input type=\"text\" id=\""+familyNameFieldId+"\" class=\"jaffa-field\" />");
            
            var emailFieldId= this.field+"foaf:email";
            ui.append("<label for=\""+emailFieldId+"\" class=\"widgetLabel peopleWidgetLabel\">Email</label>");
            ui.append("<input type=\"text\" id=\""+emailFieldId+"\" class=\"jaffa-field\" />");

            var dcIdentifierId = this.field+"dc:identifier";
            ui.append("<input type=\"hidden\" id=\""+dcIdentifierId+"\" class=\"jaffa-field\" />");
            
            var dlg_source = this.getConfig("source");
            if (dlg_source == null) { dlg_source = 'mint'; }
            ui.append("<a onclick='showMintNlaLookupDialog(this,\""+dlg_source+"\");return false;' class='mintNlaLookup' href='#'>lookup</a>");
            if (lookup_only) $("[id='" + this.id() + "'] input").attr('disabled','disabled');
            // Are we tying any data lookups to the control?
            var lookupData = this.getConfig("lookup-data");
            if (lookupData != null) {
                var lookupParser = this.getConfig("lookup-parser");
                var source = null;
                var select = null;
                // A simple lookup
                if (lookupParser == null) {
                    source = lookupData;


                // This could get complicated...
                } else {
                    // How to build a request
                    var requestConfig = this.getConfig("lookup-request") || {};
                    var requestType  = requestConfig["data-type"] || "json";
                    var requestField = requestConfig["term-field"] || "q";
                    var requestQuote = requestConfig["term-quote"];
                    if (requestQuote !== false) {
                        requestQuote = true;
                    }

                    // How to parse a response
                    var responseParser = this.getConfig("lookup-parser") || {};
                    var resultsPath = responseParser["results-path"] || [];

                    var thisWidget = this;
                    source = function(request, response) {
                        var data = {};
                        if (requestQuote)  {
                            data[requestField] = '"' + request.term + '"';
                        } else {
                            data[requestField] = request.term;
                        }

                        $.ajax({
                            url: lookupData,
                            data: data,
                            dataType: requestType,
                            contentType: "application/json; charset=utf-8",
                            success: function(data) {
                                // Find the 'node' containing our list of items
                                var results = thisWidget.dataGetOnJsonPath(data, resultsPath);
                                if (results == null) {
                                    jaffa.logWarning("Error parsing response from lookup in widget '"+thisWidget.getId()+"', cannot find results on configured data path.");
                                    response({});
                                    return;
                                }

                                // Fixes scope of 'this'
                                function mapWrap(item) {
                                    return thisWidget.perItemMapping(item);
                                }

                                // Map and return
                                response($.map(results, mapWrap));
                            }
                        });
                    }
                    select = thisWidget.onSelectItemHandling;
                }
            }

            jaffa.form.addField(titleFieldId,  this.id());
            jaffa.form.addField(givenNameFieldId,  this.id());
            jaffa.form.addField(familyNameFieldId,  this.id());
            jaffa.form.addField(emailFieldId,  this.id());
            jaffa.form.addField(dcIdentifierId,  this.id());
            

            // Add help content
            this._super();

            // Complicated validation gets preference
            var v2Rules = this.getConfig("v2Rules");
            if (v2Rules != null) {
                // Error message toggling
                var v2messages = $("<div class=\"jaffaValidationError\"></div>");
                ui.append(v2messages);
                v2messages.hide();
                var rules = this.v2rules;
                function v2invalid(fieldId, testsFailed) {
                    v2messages.html("");
                    var len = testsFailed.length;
                    for (var i = 0; i < len; i++) {
                        var key = testsFailed[i];
                        var message = rules[key].message || "Validation rule '"+key+"' failed.";
                        v2messages.append("<p>"+message+"</p>");
                    }
                    ui.addClass("error");
                    v2messages.show();
                }
                function v2valid(fieldId, testsPassed) {
                    ui.removeClass("error");
                    v2messages.html("");
                    v2messages.hide();
                }
                // Rule integration with Jaffa
                var rulesList = [];
                for (var key in v2Rules) {
                    // Store it for use later
                    this.v2rules[key] = v2Rules[key];
                    rulesList.push(key);
                    // Add the rule to Jaffa
                    jaffa.valid.addNewRule(key, this.v2rules[key].validator, this.v2rules[key].params);
                }
                // Now set these rules against our field
                jaffa.valid.setSubmitRules(this.field, rulesList, v2valid, v2invalid);

            // What about a basic mandatory flag?
            } else {
                var mandatory = this.getConfig("mandatory");
                var mandatoryOnSave = this.getConfig("mandatory-on-save");
                if (mandatory === true || mandatoryOnSave === true) {
                    // Error message creation
                    var validationText = this.getConfig("validation-text") || "This field is mandatory";
                    var validationMessage = $("<div class=\"jaffaValidationError\">"+validationText+"</div>");
                    ui.append(validationMessage);
                    // Error message toggling
                    validationMessage.hide();
                    function invalid(fieldId, testsFailed) {
                        ui.addClass("error");
                        validationMessage.show();
                    }
                    function valid(fieldId, testsPassed) {
                        ui.removeClass("error");
                        validationMessage.hide();
                    }
                    // Notify Jaffa about what we want
                    if (mandatory === true) {
                        jaffa.valid.setSubmitRules(this.field, ["required"], valid, invalid);
                    }
                    if (mandatoryOnSave === true) {
                        jaffa.valid.setSaveRules(this.field, ["required"], valid, invalid);
                    }
                }
            }

            // Add our custom classes
            this.applyBranding(ui);
        },

        // If any of the fields we told Jaffa we manage
        //   are changed it will call this.
        change: function(fieldName, isValid) {
            if (fieldName == this.field && this.labelField != null) {
                var label = jaffa.form.field(fieldName).find(":selected").text();
                jaffa.form.value(this.labelField, label);
            }
        },

        // Constructor... any user provided config and the
        //    jQuery container this was called against.
        init: function(config, container) {
            this._super(config, container);
        }
    });

    // *****************************************
    // Let Jaffa know how things hang together. 'jaffaPeople' is how the
    //   developer can create a widget, eg: $("#id").jaffaPeople();
    // And the class links to the above variable that is a valid widget
    //   implementation, extending the Jaffa bas widget.
    jaffa.widgets.registerWidget("jaffaPeople", textClass);
}
$.requestWidgetLoad(PeopleWidgetBuilder);

var PeopleRepeatableWidgetBuilder = function($, jaffa) {
    var textRepeatableClass = jaffa.widgets.listWidget.extend({
        init: function(config, container) {
            this._super(config, container);
            // Make sure 'listWidget' knows how to create each element
            this.childCreator("jaffaPeople");
        }
    });
    jaffa.widgets.registerWidget("jaffaPeopleRepeatable", textRepeatableClass);
}
$.requestWidgetLoad(PeopleRepeatableWidgetBuilder);
