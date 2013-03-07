var ReportCriteriaWidgetBuilder = function($, jaffa) {
    var reportCriteriaClass = jaffa.widgets.baseWidget.extend({
        field: null,
        oldField: null,
        v2rules: {},

        deleteWidget: function() {
            jaffa.form.ignoreField(this.field+'logicalOp');
            jaffa.form.ignoreField(this.field+'dropdown');
            jaffa.form.ignoreField(this.field+'dropdown-input');
            jaffa.form.ignoreField(this.field+'searchcomponent');
            jaffa.form.ignoreField(this.field+'match_contains');
            jaffa.form.ignoreField(this.field+'include_nulls');
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
            container.find("select[id=\""+this.oldField+"logicalOp\"]").attr("id", this.field+"logicalOp");
            container.find("span[id=\""+this.oldField+"dropdown-span\"]").attr("id", this.field+"dropdown-span");
            container.find("select[id=\""+this.oldField+"dropdown\"]").attr("id", this.field+"dropdown");
            container.find("select[id=\""+this.oldField+"dropdown-input\"]").attr("id", this.field+"dropdown-input");
            container.find("span[id=\""+this.oldField+"searchcomponent-span\"]").attr("id", this.field+"searchcomponent-span");
            container.find("[id=\""+this.oldField+"searchcomponent\"]").attr("id", this.field+"searchcomponent");
            container.find("select[name=\""+this.oldField+"match_contains\"]").attr("id", this.field+"match_contains");
            container.find("span[name=\""+this.oldField+"containsdropdown-span\"]").attr("id", this.field+"containsdropdown-span");
            container.find("select[name=\""+this.oldField+"include_nulls\"]").attr("id", this.field+"include_nulls");
            container.find("span[name=\""+this.oldField+"includeNullsDropDown-span\"]").attr("id", this.field+"includeNullsDropDown-span");
            // Tell Jaffa to ignore the field's this widget used to manage A
            jaffa.form.ignoreField(this.oldField);
            var idValue = this.id();
			$("[id='"+this.field+"dropdown-span']").on("change","[id='"+this.field+"dropdown']",function(){
												
												var optionValue = jQuery.parseJSON($(this).val());
													var id = $(this).attr('id');
													var field = id.substr(0,id.length - 8);
													//clear existing dropdowns
													$("[id=\""+field+"containsdropdown-span\"]").html("");
													jaffa.form.ignoreField(field+"match_contains", false);
													$("[id=\""+field+"includeNullsDropDown-span\"]").html("");
													jaffa.form.ignoreField(field+"include_nulls", false);
													for(key in optionValue) {
													  var options = optionValue[key];
													  if($("[id='"+field+"dropdown-input']").val() == options["key"] && $('[id="'+field+'searchcomponent"]').length > 0){
													     break;
													  }
													  options["field"] = field+"searchcomponent";
													  $("[id='"+field+"searchcomponent-span']")[key](options);
													  jaffa.form.addField(field+"searchcomponent", idValue);
													  $("[id='"+field+"dropdown-input']").val(options["key"]);
													  
													  if(options["showContainsDropDown"] != "false") {
													  	$("[id=\""+field+"containsdropdown-span\"]").html("<select id=\""+field+"match_contains\"><option value=\"field_match\">Exact match</option><option value=\"field_contains\">Match contains</option></select>"); 
													  	jaffa.form.addField(field+"match_contains", idValue);
													  }
													  if(options["showNullDropDown"] != "false") {
													  	$("[id=\""+field+"includeNullsDropDown-span\"]").html("<select id=\""+field+"include_nulls\"><option value=\"field_include_null\">Include null values</option><option value=\"field_exclude_null\">Exclude null values</option></select>");
													  	jaffa.form.addField(field+"include_nulls",  idValue); 
													  }
													}
													
												});
			
			 
			// Don't want to show the logic operator element if it's the first element in the list
            var count = this.field[this.field.length -2]; 												
			if(count == '1') {
				container.find("select[id=\""+this.field+"logicalOp\"]").hide();	
			} else {
				container.find("select[id=\""+this.field+"logicalOp\"]").show();
			}
            // TODO: Testing
        },
        // Notify Jaffa that field <=> widget relations need to be updated
        //  This is called separately from above to avoid duplicate IDs that
        //   may occur whilst DOM alterations are occuring
        jaffaUpdate: function() {
            // Only synch if an update has effected this widget
            if (this.oldField != null) {
                this._super();
                jaffa.form.addField(this.field, this.id());
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

			var logicOperatorDropDown = $('<div style="display:inline; margin-right:10px"><select class="jaffa-field" id="'+this.field+'logicalOp" name="logicalOp"><option value="AND">AND</option><option value="OR">OR</option></select>');
			ui.append(logicOperatorDropDown);
            // Label
            var label = this.getConfig("label");
            if (label != null) {
                ui.append("<label for=\""+this.field+"\" class=\"widgetLabel\">"+label+"</label>");
            }

            // Control
            var input = null;
            
            var type = this.getConfig("type") || "text";
            input = $("<span id=\""+this.field+"dropdown-span\"></span><input  type=\"hidden\" id=\""+this.field+"dropdown-input\" />");
            ui.append(input);
            input = $("<span id=\""+this.field+"searchcomponent-span\"></span><span id=\""+this.field+"containsdropdown-span\" ></span><span id=\""+this.field+"includeNullsDropDown-span\" ></span>");
            ui.append(input);
            
            var dropdownElement = $("[id='"+this.field+"dropdown-span']").jaffaDropDown({
    							"field": this.field+"dropdown",
    							"json-data-url": this.getConfig("json-data-url"),
        						"data-id-key":"value",
        						"data-label-key":"label",
        						"data-list-key":"results",
        					    "label": "",
        					    });

			var idValue = this.id();
			$("[id='"+this.field+"dropdown-span']").on("change","[id='"+this.field+"dropdown']",function(){
												
												var optionValue = jQuery.parseJSON($(this).val());
													var id = $(this).attr('id');
													var field = id.substr(0,id.length - 8);
													//clear existing dropdowns
													$("[id=\""+field+"containsdropdown-span\"]").html("");
													jaffa.form.ignoreField(field+"match_contains", false);
													$("[id=\""+field+"includeNullsDropDown-span\"]").html("");
													jaffa.form.ignoreField(field+"include_nulls", false);
													for(key in optionValue) {
													  var options = optionValue[key];
													  if($("[id='"+field+"dropdown-input']").val() == options["key"] && $('[id="'+field+'searchcomponent"]').length > 0){
													     break;
													  }
													  options["field"] = field+"searchcomponent";
													  $("[id='"+field+"searchcomponent-span']")[key](options);
													  jaffa.form.addField(field+"searchcomponent", idValue);
													  $("[id='"+field+"dropdown-input']").val(options["key"]);
													  
													  if(options["showContainsDropDown"] != "false") {
													  	$("[id=\""+field+"containsdropdown-span\"]").html("<select id=\""+field+"match_contains\"><option value=\"field_match\">Exact match</option><option value=\"field_contains\">Match contains</option></select>"); 
													  	jaffa.form.addField(field+"match_contains", idValue);
													  }
													  if(options["showNullDropDown"] != "false") {
													  	$("[id=\""+field+"includeNullsDropDown-span\"]").html("<select id=\""+field+"include_nulls\"><option value=\"field_include_null\">Include null values</option><option value=\"field_exclude_null\">Exclude null values</option></select>");
													  	jaffa.form.addField(field+"include_nulls",  idValue); 
													  }
													}
												});
			
					
					
            // Don't want to show the logic operator element if it's the first element in the list			 												
			if(this.field[this.field.length -2] == '1') {
				$("select[id=\""+this.field+"logicalOp\"]").hide();	
			}
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
            
            jaffa.form.addField(this.field+"logicalOp",  this.id());
            jaffa.form.addField(this.field+"dropdown-input",  this.id());
            jaffa.form.addField(this.field+"dropdown",  this.id());

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
    // Let Jaffa know how things hang together. 'jaffaReportCriteria' is how the
    //   developer can create a widget, eg: $("#id").jaffaReportCriteria();
    // And the class links to the above variable that is a valid widget
    //   implementation, extending the Jaffa bas widget.
    jaffa.widgets.registerWidget("jaffaReportCriteria", reportCriteriaClass);
}
$.requestWidgetLoad(ReportCriteriaWidgetBuilder);

var ReportCriteriaRepeatableWidgetBuilder = function($, jaffa) {
    var textRepeatableClass = jaffa.widgets.listWidget.extend({
        init: function(config, container) {
            this._super(config, container);
            // Make sure 'listWidget' knows how to create each element
            this.childCreator("jaffaReportCriteria");
        }
    });
    jaffa.widgets.registerWidget("jaffaReportCriteriaRepeatable", textRepeatableClass);
}
$.requestWidgetLoad(ReportCriteriaRepeatableWidgetBuilder);
