var FundingBodyWidgetBuilder = function($, jaffa) {
    var fundingBodyClass = jaffa.widgets.baseWidget.extend({
        field: null,
        oldField: null,
        v2rules: {},

        deleteWidget: function() {
            jaffa.form.ignoreField(this.field);
            jaffa.form.ignoreField(this.field+"skos:prefLabel");
            jaffa.form.ignoreField(this.field+"dc:identifier");
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
            container.find("input[id=\""+this.oldField+"skos:prefLabel\"]").attr("id", this.field+"skos:prefLabel");
            container.find("input[id=\""+this.oldField+"dc:identifier\"]").attr("id", this.field+"dc:identifier");
            // Tell Jaffa to ignore the field's this widget used to manage
            jaffa.form.ignoreField(this.oldField);
            jaffa.form.ignoreField(this.oldField+"skos:prefLabel");
            jaffa.form.ignoreField(this.oldField+"dc:identifier");
            // TODO: Testing
        },
        // Notify Jaffa that field <=> widget relations need to be updated
        //  This is called separately from above to avoid duplicate IDs that
        //   may occur whilst DOM alterations are occuring
        jaffaUpdate: function() {
            // Only synch if an update has effected this widget
            if (this.oldField != null) {
                this._super();
                jaffa.form.addField(this.field+"skos:prefLabel", this.id());
            	jaffa.form.addField(this.field+"dc:identifier", this.id());
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

            // Label
            var label = this.getConfig("label");
            if (label != null) {
                ui.append("<label for=\""+this.field+"\" class=\"widgetLabel\">"+label+"</label>");
            }


            // Control
            var type = this.getConfig("type") || "text";
            var input = $("<input type=\""+type+"\" id=\""+this.field+"skos:prefLabel\" />");

            var placeHolder = this.getConfig("placeholder");
            if  (placeHolder != null) {
              	input.attr("placeholder", placeHolder);
            }

            var size = this.getConfig("size");
            if  (size != null){
            	input.attr("size", size);
            }

            var classList = this.getConfig("class-list");
            if  (classList != null){
              	input.attr("class", classList)
            }

            ui.append(input);
            
            // Save current value of element
  			input.attr('oldVal', input.val());
   			// Look for changes in the value
   			var fieldId = this.field;
   			input.bind("propertychange keyup input paste", function(event){
      				// If value has changed...
      				if (input.attr('oldVal') != input.val()) {
       					// Updated stored value
       					input.attr('oldVal', input.val());
       					$("[id='"+fieldId+"dc:identifier']").val('');
			     }
  		   });
            
            var hiddenInput = $("<input type=\"hidden\" id=\""+this.field+"dc:identifier\" />");
            ui.append(hiddenInput);
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
                    responseParser["outputs"][hiddenInput.attr('id')]= "${identifier}";
                    var resultsPath = responseParser["results-path"] || [];

                    var thisWidget = this;
                    source = function(request, response) {
                        var data = {};
                        var escapedRequestTerm = encodeURIComponent(request.term.toLowerCase());
                        if (requestQuote)  {
                            data[requestField] = '"' + escapedRequestTerm + '"';
                        } else {
                            data[requestField] = escapedRequestTerm;
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
                                    jaffa.logWarning("Error parsing response from lookup in widget '"+thisWidget.id()+"', cannot find results on configured data path.");
                                    response({});
                                    return;
                                }

                                // Fixes scope of 'this'
                                function mapWrap(item) {
                                    return thisWidget.perItemMapping(item);
                                }

                                // Map and return
                                response($.map(results, mapWrap));
                            },
                            "error": function (jqHXR, textStatus, error) {
                            	alert(error);
                            }
                        });
                    }
                    select = function(event, ui) {
                    var targetId = $(event.target).attr('id');
            	targetId = targetId.substring(0,targetId.length-15);
           		 for (var field in ui.item) {
            	
                if (field != "label" && field != "value") {
                    var value = ui.item[field];
                    var found = false;
                    // First, is the target a Jaffa field?
                    if(field.indexOf(targetId) == 0) {
                    var target = jaffa.form.field(field);
                    if (target != null) {
                        jaffa.form.value(field, value);
                        $("[id='"+field+"']").change();
                        found = true;
                    }

                    // Second, is it in our document as a selector?
                    target = $(field);
                    if (found == false && target != null) {
                    	if(target.is("input")) {
                    		target.val(value);
                    	} else {
                        	target.html(value);
                        }
                        target.change();
                        found = true;
                    }
					
                    // Hmm, log something
                    if (!found) {
                        jaffa.logWarning("Unable to send output to '"+field+"', could not find anything meaningful with that value.");
                    }
                    }

                }
            }
        };
                }

                input.autocomplete({
                    "source": source,
                    "select": select
                });
            }

            // And is there a starting value?
            var defaultValue = this.getConfig("default-value");
            if (defaultValue != null) {
                input.val(defaultValue);
            }

            jaffa.form.addField(this.field+"skos:prefLabel", this.id());
            jaffa.form.addField(this.field+"dc:identifier", this.id());

            // Add help content
            this._super();

            // Activating a change trigger will synch
            //  all fields and the managed data
            input.trigger("change");

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
    // Let Jaffa know how things hang together. 'jaffaText' is how the
    //   developer can create a widget, eg: $("#id").jaffaText();
    // And the class links to the above variable that is a valid widget
    //   implementation, extending the Jaffa bas widget.
    jaffa.widgets.registerWidget("jaffaFundingBody", fundingBodyClass);
}
$.requestWidgetLoad(FundingBodyWidgetBuilder);

var FundingBodyRepeatableWidgetBuilder = function($, jaffa) {
    var textRepeatableClass = jaffa.widgets.listWidget.extend({
        init: function(config, container) {
            this._super(config, container);
            // Make sure 'listWidget' knows how to create each element
            this.childCreator("jaffaFundingBody");
        }
    });
    jaffa.widgets.registerWidget("jaffaFundingBodyRepeatable", textRepeatableClass);
}
$.requestWidgetLoad(FundingBodyRepeatableWidgetBuilder);
