

(function(){
    var dialog=$("<div>Test dialog message!</div>").dialog({
                  title:"Name lookup",
                  height:350,  maxHeight:600,
                  width:400,
                  modal:false,
                  resizable:true,
                  position:"center",
                  draggable:true,
                  autoOpen:false
                });
    var detailDialog=$("<div/>").dialog({
                  title:"Detail information",
                  height:"auto",
                  width:400,
                  modal:false,
                  resizable:true,
                  position:"center",
                  draggable:false,
                  autoOpen:false
                });
    gdialog = dialog;


    var displayNameLookups = function(json, position, queryStr, callback){
        var div, tbody, tr, td, label, id;
        div = $("<div/>");
        if(queryStr) div.text("Search result for '" + queryStr + "'");
        div.append("<hr/>");
        div.append($("<table/>").append(tbody=$("<tbody/>")));
        $.each(json.results, function(c, result){
          var r, a;
          id="rId"+c;
          tr=$("<tr/>").append(td=$("<td/>"));
          r=$("<input type='radio' name='name' />").attr("id", id);
          r.val(JSON.stringify(result));
          label=$("<label/>").attr("for", id);
          label.append(result["rdfs:label"]);
          td.append(r);
          td.append(label);
          //
          tr.append(td=$("<td/>"));
          a=$("<a style='color:blue;' href='#'>details</a>");
          td.append(a);
          tbody.append(tr);
          label.dblclick(function(){dialog.dialog("option", "buttons").OK();});
          a.click(function(e){
            var pos = dialog.parent().position();
            pos.left += 10;
            pos.top += 20;
            displayDetails(result["rdfs:label"], result, pos, r);
            return false;
          });
        });

        dialog.html(div);
        dialog.dialog("option", "buttons", {
                        "OK":function(){
                            var value=div.find("input[name=name]:checked").val();
                            dialog.dialog("close");
                            detailDialog.dialog("close");
                            callback(true, JSON.parse(value));
                          },
                          "Cancel":function(){
                            dialog.dialog("close");
                            detailDialog.dialog("close");
                            callback(false);
                          }
                        });
        //dialog.dialog("option", "position", [position.left, position.top]);
        dialog.dialog("open");
        dialog.parent().css("top", position.top+"px").css("left", position.left+"px");
    }

    var displayDetails = function(name, details, pos, link){
        detailDialog.text(name);
        detailDialog.append("<hr/>");
        $.each(details, function(k, v){
            var d=$("<div/>");
            d.text(k+" : "+v);
            detailDialog.append(d);
        });
        detailDialog.dialog("option", "buttons", {
                            "OK": function(){link.click(); detailDialog.dialog("close");},
                            "Cancel": function(){detailDialog.dialog("close");}
                          });
        //detailDialog.dialog("option", "position", [pos.left, pos.top]);
        detailDialog.dialog("open").dialog("moveToTop");
        detailDialog.parent().css("top", pos.top+"px").css("left", pos.left+"px");
    };

//
    function init(){
        $(".nameLookup-section").each(function(c, e){
            nameLookupSection($(e));
        });
    }

    function nameLookupSection(ctx){
        var url = ctx.find(".nameLookup-url").val();
        var valueNs = ctx.find(".nameLookup-value-ns").val();
        var textNs = ctx.find(".nameLookup-text-ns").val();
        function debug(msg){
            ctx.find(".nameLookup-debugMsg").text(msg.toString());
        }
        function getJson(queryUrl, timeoutSec, callback){
            $.ajax({url:queryUrl, dataType:"json", timeout:timeoutSec*1000,
                success:callback,
                error:function(x,s,e){callback({error:s});}
            });
        }
        //ctx.find(".nameLookup-lookup").unbind().click(function(e){
        ctx.find(".nameLookup-lookup").die().live("click", function(e){
            var target, parent, queryTerm, queryUrl;
            target=$(e.target);
            gtarget = target
            parent=target.parent();
            if(parent.find(".nameLookup-name").size()==0){
                parent = parent.parent();
            }
            queryTerm = parent.find(".nameLookup-name").map(function(i, e){return e.value;});
            queryTerm = $.trim($.makeArray(queryTerm).join(" "));
            if(queryTerm==="") return false;
            // Note: double escape the parameter because it is being passed as a parameter inside a parameter
            queryUrl = url.replace("{searchTerms}", escape(escape(queryTerm)));
            debug("clicked queryUrl="+queryUrl);
            getJson(queryUrl, 6, function(json){
                function callback(ok, result){
                    debug(ok);
                    if(ok){
                        function xUpdate(ns, what){
                            var nst, k;
                            if(!ns) return;
                            nsp = ns+"-";
                            parent.find("."+ns).each(function(c, e){
                                e=$(e);
                                $.each(e.attr("class").split(/\s+/), function(_, cls){
                                    if(cls.substr(0, nsp.length)===nsp){
                                        k = cls.substr(nsp.length);
                                        if(result[k]){
                                            e[what](result[k]);
                                        }
                                    }
                                });
                            });
                        }
                        xUpdate(valueNs, "val");
                        xUpdate(textNs, "text");
                    }
                }
                if(json.error){
                    alert(json.error);
                }else{
                    //alert(json.results.length);
                    var position = target.position();
                    displayNameLookups(json, position, queryTerm, callback);
                }
            });
            return false;
        });
        debug("loaded ok");
    }

    $(function(){
        init();
    });

    nameLookup = {init:init};
})($);


