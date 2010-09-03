
var widgets={forms:[], globalObject:this};


(function($){
  var formClassName = "widget-form";

  function trim(s){
    return $.trim(s);
    return s.replace(/^\s+|\s+$/g, "")
  }

  function getById(id){
    var e=document.getElementById(id);
    if(e){
        return $(e);
    }else{
        return $("#_doesNotExist_.-_");
    }
  }

  function reduce(c, func, i){
    if(!i)i=0;
    $.each(c, function(k, v){
      i = func(v, i);
    });
    return i;
  }

  function any(c, func){
    var flag=false;
    $.each(c, function(k, v){
      if(func(v)) flag=true;
    });
    return flag;
  }

  function isFunction(func){
      return typeof(func)==="function";
  }

  function callIfFunction(func, a, b, c){
      if(typeof(func)==="function"){
          try{ func(a, b, c); }catch(e){}
      }
  }

  function messageBox(msg){
      var msgBox=messageBox.msgBox;
      if(!msgBox){  // setup
          var div, i;
          msgBox = $("<div class='box hidden' style='text-align:center;'/>");
          msgBox.append($("<span/>"));
          div = $("<div style='padding-top:1em;''/>");
          msgBox.append(div);
          i = $("<input type='button' value='OK'/>");
          div.append(i);
          messageBox.msgBox=msgBox;
          i.click(function(){msgBox.dialog("close");});
          msgBox.dialog({title:"Message", hide:"blind",
                modal:true, autoOpen:false });
      }
      msgBox.dialog("open").find("span:first").text(msg);
  }
  
  function changeToTabLayout(elem){
    var h, li, ul = $("<ul></ul>");
    elem.children("h3").each(function(c, e){
        h = $(e);
        li = $("<li><a href='#" + h.next().attr("id") + "'><span>" + h.text() + "</span></a></li>");
        ul.append(li);
        h.remove();
    });
    if(true){
        var sel;
        elem.find(".prev-tab").click(function(){
            sel=elem.tabs("option", "selected");
            elem.tabs("option", "selected", sel-1);
        });
        elem.find(".next-tab").click(function(){
            sel=elem.tabs("option", "selected");
            elem.tabs("option", "selected", sel+1);
        });
    }
    elem.prepend(ul);
    return elem;
  }

  function validator(){
    var reg1=/(\s*(\w+)\s*(\(((('([^'\\]|\\.)*')|("([^"\\]|\\.)*")|(\/([^\/\\]|\\.)*\/)|(([^'"\/\\]|\\.)*?))*?)\))\s*(;|$)\s*)|(\s*(;|$))/g; // 2, 4, 14, 15=Err
    var reg2=/(\()|(\))|('([^'\\]|\\.)*')|("([^"\\]|\\.)*")|(\/([^\/\\]|\\.)*\/)|(\w[\w\d\._]*)|(([^\(\)\w\s'"\/\\]|\\.)+)/g;
    var reg3=/(\s*(rule)\s*(\{((('([^'\\]|\\.)*')|("([^"\\]|\\.)*")|(\/([^\/\\]|\\.)*\/)|(([^'"\/\\]|\\.)*?))*?)\}))/g; // 4
    var tests={}, namedTests={};
    function iterReader(arr){
      var pos=-1; l=arr.length;
      function current(){ return arr[pos]; }
      function next(){pos+=1; return current();}
      function hasMore(){return (pos+1)<l;}
      function lookAHead(){return arr[pos+1];}
      return {current:current, next:next, hasMore:hasMore, lookAHead:lookAHead};
    }
    function isOkToX(x){
      var e=false;
      hideAllMessages();
      $.each(tests[x]||[], function(c,f){
        e|=f();
      });
      return !e;
    }
    function hideAllMessages(){$(".validation-err-msg").hide();}
    function testTest(name){
        var test=namedTests[name];
        if(test && test._testFunc){
            try{
                return !test._testFunc();
            }catch(e){
            }
        }
        return false;
    }
    function getExpr(reader){
      // tests: !=str, =str, /regex/, !/regex/, empty, notEmpty, email, date, [>1], (), ex1 AND ex2, ex1 OR ex2,
      var v=reader.next(), expr="", getNumber;
      var vl=v.toLowerCase();
      getNumber=function(){
          var v, n = NaN;
          v=reader.next();
          if(v=="("){v=reader.next();if(reader.lookAHead()==")")reader.next();}
          return v*1;
      }
      if(vl=="email"){v="/.+?\\@.+\\..+?/";}
      else if(vl=="empty"){expr="(v=='')";}
      else if(vl=="yyyy"){    v="/^[12]\\d{3}$/";}
      else if(vl=="yyyymm"){  v="/^[12]\\d{3}([\\/\\\\\\-](0?[1-9]|1[012])|((0[1-9])|(1[012])))$/";}
      else if(vl=="yyyymmdd"){v="/^[12]\\d{3}([\\/\\\\\\-](0?[1-9]|1[012])|((0[1-9])|(1[012])))([\\/\\\\\\-](0?[1-9]|[12]\\d|3[01])|((0[1-9])|[12]\\d|(3[01])))$/";}
      else if(vl=="leneq" || vl=="lengtheq"){
          var n = getNumber();
          if(isNaN(n)){ /*Error*/ return "";}
          v="/^.{"+n+"}$/"; }
      else if(vl=="lengt" || vl=="lengthgt"){
          var n = getNumber();
          if(isNaN(n)){ /*Error*/ return "";}
          v="/^.{"+(n+1)+",}$/"; }
      else if(vl=="lenlt" || vl=="lengthlt"){
          var n = getNumber();
          if(isNaN(n)){ /*Error*/ return "";}
          v="/^.{0,"+(n-1)+"}$/"; }
      if(vl=="notempty"){expr="(v!='')";}
      else if(v=="="){expr="(v=="+reader.next()+")";}
      else if(v=="!="){expr="(v!="+reader.next()+")";}
      else if(v[0]=="/"){expr="("+v+".test(v))";}
      else if(v.substr(0,2)=="!/"){expr="("+v+".test(v))";}
      else if(v=="("){expr+="("+getExpr(reader)+")";if(reader.next()!=")"){alert("expected a ')'!");}; }
      else if(/^[\w\d\._]+$/.test(v)){expr+="testTest('"+v+"')";}
      v=reader.lookAHead();
      if(v){
        v=v.toUpperCase();
        if(v=="AND"){reader.next(); expr+="&&"+getExpr(reader);}
        else if(v=="OR"){reader.next(); expr+="||"+getExpr(reader);}
      }
      return expr;
    }
    function getWhen(reader){
        var d, action, target;
        if(!reader.hasMore()) return null;
        d=reader.next();
        while(d=="," || d==";")d=reader.next();
        if(!d) return null;
        if(d[0]=="'" || d[0]=='"'){
            target=$(eval(d));
            if(reader.lookAHead()=="."){reader.next();d=reader.next();}
            else{ return {}; /* ERROR */ }
        }
        action = d.toLowerCase();
        if(action.substr(0,2)=="on")action=action.substr(2);
        while(reader.hasMore()){
            // read upto the next , or ;
            d=reader.next();
            if(d=="," || d==";") break;
        }
        return {action:action, target:target};
    }
    function setup(ctx, onLoadTest){
        var m, w, va, f, a, t;
        var validationsFor={}, valdationsForLists={};
        //var matchQuotedStr = '("([^"\\]|\\.)*")';     // continues matching until closing (unescaped) quote
        var vLabels=$("label.validation-err-msg");
        $(".validation-err-msg").hide();
        //value="for('dc:title'),notEQ(''),when(onChange)"
        function rule(v){
            var dict={};
            function match(){
                m=arguments;     //2, 4, 14, 15=Err
                if(m[0].length==0)return "";
                if(m[15]){
                    alert("Error: '"+m[15]+"' in '"+v+"'");
                    return "";
                }
                w=m[2].toLowerCase();
                va=m[4];
                dict[w]=va;
                return "";
            }
            v.replace(reg1, match);
            f=dict["for"];
            dict["when"]=(dict["when"]||"");
            if(f){
                if(/\.0(?=\.|$)/.test(dict[f])){
                    a = validationsForLists[f];
                    if(!a) a=validationsForLists[f]=[];
                }else{
                    a = validationsFor[f];
                    if(!a) a=validationsFor[f]=[];
                }
                a.push(dict);
                if(dict["name"]){
                    namedTests[dict["name"]]=dict;
                }else if(!namedTests[f]){   // default name is 'for' id
                    namedTests[f]=dict;
                }
            }
        }
        ctx.findx(".validation-rule").each(function(c, v){
            v = $(v).val() || $(v).text();
            rule(v);
        });
        ctx.findx(".validation-rules").each(function(c, v){
            v = $(v).text();
            v.replace(reg3, function(){ var v=arguments[4]; if(v)rule(v); });
        });
        $.each(validationsFor, function(f, l){
            var target = $(document.getElementById(f));
            var reader, getValue, showValidationMessage;
            var testStr, func;
            if(true){
                var vLabel=vLabels.filter("[for="+f+"]");
                getValue=function(){ return target.val(); };
                showValidationMessage=function(show){ show?vLabel.show():vLabel.hide(); return show;};

                $.each(l, function(c, d){
                    testStr="";
                    if(d.test){
                      reader = iterReader(d.test.match(reg2));
                      testStr = getExpr(reader);
                      try{
                        func="func=function(){var v=getValue();return showValidationMessage(!("+testStr+"));};";
                        eval(func);
                        d._testFunc = func;
                      } catch(e){
                        alert(e + ", func="+func);
                      }
                      //if(onLoadTest){func();}
                      m = d.when.match(reg2);
                      if(m){
                        reader = iterReader(m);
                        while(w=getWhen(reader)){
                          w.target = w.target||target;
                          w.target.bind(w.action, func);
                          if(!tests[w.action]) tests[w.action]=[];
                          tests[w.action].push(func);
                        }
                      }
//                      $.each(d.when.split(/(,|\s)+/), function(c, w){
//                        if(w.substr(0,2)=="on") w=w.substr(2);
//                        target.bind(w, func);
//                        if(!tests[w]) tests[w]=[];
//                        tests[w].push(func);
//                      });
                    }
                });
            }
        });
    }
    return {
      setup:setup,
      test:function(){},
      isOkToSave:function(){return isOkToX("save");},
      isOkToSubmit:function(){return isOkToX("submit");},
      hideAllMessages:hideAllMessages,
      parseErrors:{}
    }
  }
  widgets.validator = validator;
  
  function formWidget(ctx){
      var widgetForm={};
      var validator;
      var listeners={};
      var ctxInputs;

      function addListener(name, func){
          var l;
          l=listeners[name];
          if(!l){
              l = [];
              listeners[name]=l;
          }
          l.push(func);
      }
      function removeListener(name, func){
          var l, i;
          l=listeners[name]||[];
          i=$.inArray(name, l);
          if(i>-1)l.splice(i, 1);
      }
      function removeListeners(name){
          delete listeners[name];
      }
      function raiseEvents(name){
          var l=listeners[name]||[];
          for(var k in l){
              var f = l[k];
              try{
                  if(f()===false) return false; // cancel event
              }catch(e){}
          }
      }

      function onSubmit(){
        if(raiseEvents("onSubmit")==false){
            return false;
        }
        submit();
        return true;
      }
      function onSave(){
        if(raiseEvents("onSave")==false){
            return false;
        }
        save();
        return true;
      }
      function onRestore(data){
        if(raiseEvents("onRestore")==false){
            return false;
        }
        //messageBox(JSON.stringify(data))
        restore(data);
        return true;
      }
      function onReset(data){
        if(raiseEvents("onReset")==false){
            return false;
        }
        reset(data);
        return true;
      }

      function submit(){
          submitSave("submit");
      }

      function save(){
          submitSave("save");
      }

      function submitSave(stype){
        var data, url, replaceFunc;
        var xFunc, xResultFunc;
        replaceFunc=function(s){
            s = s.replace(/[{}()]/g, "");   // make it safe - no function calls
            return eval(s);
        };
        xFunc = widgets.globalObject[ctx.findx("."+stype+"-func").val()];
        xResultFunc = widgets.globalObject[ctx.findx("."+stype+"-result-func").val()];
        callIfFunction(xFunc, widgetForm);
        data = getFormData();
        url = ctx.findx(".form-fields-"+stype+"-url").val();
        url = url.replace(/{[^}]+}/g, replaceFunc);
        function completed(data){
            if(typeof(data)=="string"){
                try{
                    data = JSON.parse(data);
                }catch(e){
                    data = {error:e};
                }
            }
            callIfFunction(xResultFunc, widgetForm, data);
            if(data.error || !data.ok){
                if(!data.ok && !data.error) data.error="Failed to receive an 'ok'!";
                messageBox("Failed to "+stype+"! (error='"+data.error+"')");
            }else{
                if(stype=="save"){
                    ctx.findx(".saved-result").text("Saved OK").
                        css("color", "green").show().fadeOut(4000);
                }else if(stype=="submit"){
                    ctx.findx(".submitted-result").text("Submitted OK").
                        css("color", "green").show().fadeOut(4000);
                }
            }
        }
        if(data.title===null)data.title=data["dc:title"];
        if(data.description===null)data.description=data["dc:description"];
        if(widgetForm.hasFileUpload){
            var elems=[], h=$("<input type='text' name='json' />");
            var fileSubmitter = createFileSubmitter();
            h.val(JSON.stringify(data));
            elems.push(h[0]);
            ctx.findx("input[type=file]").each(function(c, f){
                elems.push(f);
            });
            fileSubmitter.submit(url, elems, completed);
        }else{
            // data.json = JSON.stringify(data);
            $.ajax({type:"POST", url:url, data:data,
                success:completed,
                error:function(xhr, status, e){ completed({error:"status='"+status+"'"}); },
                dataType:"json"
            });
        }
      }

      function getFormData(){
        var data={}, s, v, e, formFields;
        formFields = ctx.findx(".form-fields").val() +","+ ctx.findx(".form-fields-readonly").val();
        formFields = $.grep(formFields.split(/[\s,]+/),
                                function(i){return /\S/.test(i)});
        function getValue(i){
          e = getById(i);
          if(e.size()==0) e=ctxInputs.filter("[name="+i+"]");
          if(e.size()==0){return null;}
          v = e.val();
          if(e.attr("type")==="checkbox"){
            if(!e.attr("checked"))v="";
          } else if(e.attr("type")==="radio"){
            v = e.filter(":checked").val();
          }
          return v;
        }
        $.each(formFields, function(c, i){
          s = /\.0+(\.|$)/.test(i);
          if(s){
            var id, count=1;
            while(true){
             try{
              id = i.replace(/\.0(?=\.|$)/, "."+count);
              v=getValue(id);
              if(v===null) break;
              data[id]=v;
              count+=1;
             } catch(e){
                 alert(e);
                 throw e;
             }
            }
          }else{
            v=getValue(i);
            data[i]=v;
          }
        });
        if(data.metaList=="[]" || data.metaDataList=="[]"){
            s = [];
            $.each(data, function(k, v){if(k!="metaList")s.push(k);});
            if(data.metaList=="[]"){ data.metaList=s; }
            if(data.metaDataList=="[]"){ data.metaDataList=s; }
        }
        return data;
      }

      function restore(data){
          var keys=[], skeys=[], input, t;
          var formFields = $.grep(ctx.findx(".form-fields:first").val().split(/[\s,]+/),
                                function(i){return /\S/.test(i)});
          $.each(data, function(k, v){keys.push(k);});
          keys.sort();
          skeys = $.grep(keys, function(i){return /\.\d+(\.|$)/.test(i);}, true);
          $.each(skeys, function(c, v){
              if($.inArray(v, formFields)!=-1){
                  ctxInputs.filter("[id="+v+"]").val(data[v]);
              }
          });
          // list items
          skeys = $.grep(keys, function(i){return /\.\d+(\.|$)/.test(i);});
          $.each(skeys, function(c, v){
              var k = v.replace(/\.\d+(?=(\.|$))/, ".0");
              if($.inArray(k, formFields)!=-1){
                  input = ctxInputs.filter("[id="+v+"]");
                  if(input.size()>0){
                    input.val(data[v]);
                  }else{
                    input = ctxInputs.filter("[id="+k+"]");
                    t=input.parents(".input-list:first").find(".add-another-item, .item-add");
                    if(t[0].forceAdd){
                        t[0].forceAdd();
                    }else{
                        t.click();
                    }
                    // update inputs - this could be done better
                    ctxInputs = ctx.findx("input, textarea, select");
                    input = ctxInputs.filter("[id="+v+"]");
              if(input.size()==0){
                  alert("id '"+v+"' not found!");
              }
                    input.val(data[v]);
                  }
              }
          });
      }

      function reset(data){
          if(!data)data={};
          
      }


      function setupFileUploader(fileUploadSections, onChange){
        if(!fileUploadSections) fileUploadSections=ctx.findx(".file-upload-section");
        fileUploadSections.each(function(c, e){
            var handleFileDrop;
            var ifile, fileUploadSection;
            fileUploadSection = $(e);
            ifile = fileUploadSection.find("input[type=file]");
            if(!onChange){
                onChange=function(fileInfo, fileUploadSection){
                    var s;
                    s=["<span>", fileInfo.typeName, ": ", fileInfo.name, " (",
                        fileInfo.kSize, "k) </span>"];
                    s = $(s.join(""));
                    if(fileInfo.createImage) s.append(fileInfo.createImage());
                    fileUploadSection.find(".file-upload-info").html(s);
                };
            }
            ifile.change(function(e){
                var fileInfo=getFileUploadInfo(e.target.files[0]);
                onChange(fileInfo, fileUploadSection);
            });
            fileUploadSection.bind("dragover", function(ev){
                if(ev.target.tagName=="INPUT"){ return true; }
                ev.stopPropagation(); ev.preventDefault();
            });
            handleFileDrop=function(ev){
                var file, fileInfo;
                if(ev.target.tagName=="INPUT"){ return true; }
                ev.stopPropagation(); ev.preventDefault();
                file=ev.dataTransfer.files[0];
                fileInfo=getFileUploadInfo(file);
                onChange(fileInfo, fileUploadSection);
                ifile.val("");      // reset
                //gDroppedFile=file;
                //ifile[0].files[0]=file;
                return;
            }
            //fileUploadSection.bind("drop", handleFileDrop);  // Note: binding to the wrong 'drop' event!
            if(fileUploadSection[0].addEventListener){
                fileUploadSection[0].addEventListener("drop", handleFileDrop, false);
            }
        });
      }

      function getFileUploadInfo(file){
        var fileInfo = {};
        fileInfo.file = file;
        fileInfo.size = file.size;
        fileInfo.kSize = parseInt(file.size/1024+0.5);
        fileInfo.type = file.type;
        fileInfo.name = file.name;
        try{
            fileInfo.encodedData=file.getAsDataURL();
        }catch(e){ }
        if(file.type.search("image/")==0){
            fileInfo.image=true;
            fileInfo.typeName = "Image";
            if(fileInfo.encodedData){
                fileInfo.createImage=function(){
                    var i;
                    i=$("<img class='thumbnail' style='vertical-align:middle;'/>");
                    i.attr("src", fileInfo.encodedData);
                    i.attr("title", fileInfo.name);
                    return i;
                };
            }
        }else if(file.type.match("video|flash")){
            fileInfo.video=true;
            fileInfo.typeName = "Video";
        }else if(file.type.match("text|pdf|doc|soffice|rdf|txt|opendocument")){
            fileInfo.document=true;
            fileInfo.typeName = "Document";
        }else{
            fileInfo.typeName = "File";
        }
        return fileInfo;
      }

      function createFileSubmitter(){
          var iframe, getBody, submit;
          iframe = $("<iframe id='upload-iframe' style='display:none; height:8ex; width:80em; border:1px solid red;'/>");
          $("body").append(iframe);
          if(iframe[0].contentDocument){
              getBody=function(){ return $(iframe[0].contentDocument.body); };
          }else{
              getBody=function(){ return $(iframe[0].contentWindow.document.body); };
          }
          submit=function(url, elems, callback){
              // callback(resultText, iframeBodyElement);
              var form = $("<form method='POST' enctype='multipart/form-data' />");
              iframe.unbind();
              if(!url)url=window.location.href+"";
              form.attr("action", url);
              $.each(elems, function(c, e){
                  var c=$(e).clone();
                  if(c.attr("name")===""){c.attr("name", e.id);}
                  form.append(c);
              });
              getBody().append(form);
              setTimeout(function(){
                  iframe.load(function(){
                      var ibody=getBody();
                      callback(ibody.text(), ibody);
                  });
                  form.submit();
              }, 10);
          };
          // submit(url, elems, callback)
          //    url = url to sumbit to
          //    elems = 'input' elements to be submitted (cloned)
          //    callback = function(textResult, iframeBody)
          return {submit:submit, iframe:iframe, getBody:getBody};
      }

      // TODO: remove table, tbody, tr and td references, just rely on the classes
      function listInput(c, i){
          var table, count, tmp, visibleItems, displayRowTemplate, displaySelector;
          var add, del, reorder, addUniqueOnly=false;
          table = $(i);
          if(table.hasClass("sortable")){
            table.find("tbody:first").sortable({
              items:"tr.sortable-item",
              update:function(e, ui){ reorder(); }
            });
          }
    // check all variable names
          if(table.find(".item-display").size()){
            if(table.find("tr.item-input-display").size()){
              alert("Error: table.input-list can not have both 'item-display' and 'item-input-display' table row classes");
              return;
            }
            // For handling 'item-display' (where there is a separate/special row for handling the display of added items)
            //    Note: if there is an 'item-display' row then it is expected that there will also be an
            //        'item-input' row as well an 'item-add' button/link
            displaySelector = ".item-display";
            tmp=table.find(displaySelector).hide();
            displayRowTemplate=tmp.eq(0);
            add=function(e, force){
              // get item value(s) & validate (if no validation just test for is not empty)
              var values=[];
              var test=[];
              table.find("tr.item-input input[type=text]").each(function(c, i){
                values[c]=[$.trim($(i).val()), i.id];
                test[c]=values[c][0];
                $(i).val("");   // reset
              }).eq(0).focus();
              //
              visibleItems = table.find(displaySelector+":visible");
              if(!force){
                  if(!any(values, function(v){ return v[0]!==""; })) return;
                  if(addUniqueOnly){
                    // Check that this entry is unique
                    var unique=true;
                    visibleItems.each(function(c, i){
                      i=$(i);
                      var same=true;
                      i.find("input").each(function(c2, i){
                        if(test[c2]!=i.value)same=false;
                      });
                      if(same)unique=false;
                    });
                    if(!unique){
                        alert("Selection is already in the list. (not a unique value)");
                        return;
                    }
                  }
              }

              tmp = displayRowTemplate.clone().show();
              count = visibleItems.size()+1;
              tmp.find("*[id]").each(function(c, i){
                  //$(i).addClass(i.id);
                  i.id = i.id.replace(/\.0(?=\.|$)/, "."+count);
              });
              tmp.find(".item-display-item").each(function(c, i){
                var id = values[c][1].replace(/\.0(?=\.|$)/, "."+count);
                //$(i).text(values[c][0]);
                //$(i).append("<input type='hidden' id='"+id+"' value='"+values[c][0]+"'/>");
                $(i).append("<input type='text' id='"+id+"' value='"+values[c][0]+
                            "' readonly='readonly' size='64' />");
              });
              tmp.find(".sort-number").text(count);
              table.find(displaySelector+":last").after(tmp);
              visibleItems.find(".delete-item").show();
              //if(count==1) tmp.find(".delete-item").hide();
              tmp.find(".delete-item").click(del);
            }

            del=function(e){
              $(this).parents("tr").remove();
              //if(table.find(displaySelector+":visible").size()==1){
              //  table.find(displaySelector+":visible .delete-item").hide();
              //}
              reorder();
              return false;
            }

            table.find(".item-add").click(add);
            table.find(".item-add")[0].forceAdd = function(){add(null, true);};
            addUniqueOnly = table.find(".item-add").hasClass("add-unique-only");
            table.find("tr.item-input input[type=text]:last").keypress(function(e){
              if(e.which==13){
                add();
              }
              if(e.which==8 && false){      // backspace delete/recall exp.
                if($(e.target).val()==""){
                  if(table.find(displaySelector+":visible").size()>0){
                    var i=table.find(displaySelector+":visible:last input:last");
                    del.apply(i);
                    $(e.target).val(i.val());
                    return false;
                  }
                }
              }
            });
          }else if(table.find("tr.item-input-display").size()){
            // For handling 'item-input-display' type lists
            //   Note: if there is an 'item-input-display' row then it is also excepted that there
            //      will be an 'add-another-item' button or link
            displaySelector="tr.item-input-display";
            tmp=table.find(displaySelector).hide();
            displayRowTemplate=tmp.eq(0);

            add=function(){
              visibleItems = table.find(displaySelector+".count-this");
              tmp = displayRowTemplate.clone().show().addClass("count-this");
              count = visibleItems.size()+1;
              tmp.find("*[id]").each(function(c, i){
                  //$(i).addClass(i.id);
                  i.id = i.id.replace(/\.0(?=\.|$)/, "."+count);
              });
              tmp.find(".sort-number").text(count);
              table.find(displaySelector+":last").after(tmp);
              visibleItems.find(".delete-item").show();
              if(count==1) tmp.find(".delete-item").hide();
              tmp.find(".delete-item").click(del);
            }

            del=function(e){
              $(this).parents("tr").remove();
              if(table.find(displaySelector+":visible").size()==1){
                table.find(displaySelector+":visible .delete-item").hide();
              }
              reorder();
              return false;
            }

            add();
            table.find(".add-another-item").click(add);
          }

          reorder=function(){
            table.find(displaySelector+":visible").each(function(c, i){
              $(i).find("*[id]").each(function(_, i){
                i.id = i.id.replace(/\.\d+(?=\.|$)/, "."+(c+1));
              });
              $(i).find(".sort-number").text(c+1);
            });
          }
      }

      // ==============
      // Multi-dropdown selection
      // ==============
      function buildSelectList(json, parent, getJson, onSelection){
          var s, o, children={}, ns, selectable;
          ns = (json.namespace || "") || (parent.namespace || "");
          selectable = (json.selectable==null)?(!!parent.selectable):(!!json.selectable);
          s = $("<select/>");
          if(!json["default"]){
            o = $("<option value=''>Please select one</option>");
            s.append(o);
          }
          $.each(json.list, function(c, i){
            var sel=!!(i.selectable!=null?i.selectable:selectable);
            children[i.id]={url:(i.children==1?i.id:i.children), label:i.label, id:i.id,
                            selectable:sel, namespace:ns, parent:parent};
            o = $("<option/>");
            o.attr("value", i.id);
            if(i.id==json["default"]) o.attr("selected", "selected");
            o.text(i.label);
            s.append(o);
          });
          function onChange(){
            var id, child, j;
            id = s.val();
            child = children[id] || {parent:parent};
            if(s.nextUntil){
                s.nextUntil(":not(select)").remove();
            }else{
                function removeSelects(s){
                    if(s.size()==0)return;
                    removeSelects(s.next("select"));
                    s.remove();
                }
                removeSelects(s.next("select"));
            }
            if(child.url){
              getJson(child.url, false, function(j){
                  s.after(buildSelectList(j, child, getJson, onSelection));
                  onSelection(child);
              });
            }
            onSelection(child);
          }
          s.change(onChange);
          setTimeout(onChange, 10);
          return s;
      }

      function sourceDropDown(c, dsdd){
          var ds=$(dsdd), id=dsdd.id, jsonUrl, json=[], selAdd;
          var selAddNs, selAddId, selAddLabel;
          var getJson, onSelection, onJson;
          ds.hide();
          selAdd = ds.parent().find(".selection-add");
          // ".json-data-source-url" val(), ".json-data-source" text(),
          //    ".selection-add"
          getJson = function(urlId, absolute, onJson){
            var j, url=urlId;
            if(json) j=json[urlId]
            if(j){
                onJson(j);
                return;
            }
            if(!absolute){
              url=jsonUrl+urlId;
              if(!/\.json$/.test(url)) url+=".json";
            }
            $.getJSON(url, function(data){
              json=data;
              onJson(json);
            });
          }
          onSelection = function(info){
            var sel;
            //info.namespace, info.id, info.label, info.selectable, info.parent
            while(info.selectable!==false && info.selectable!==true){
              if(info.parent) info = info.parent;
              else info.selectable=false;
            }
            sel=info.selectable;
            if(/BUTTON|INPUT/.test(selAdd[0].tagName)){
              selAdd.attr("disabled", sel?"":"disabled");
            }else{
              sel?selAdd.show():selAdd.hide();
            }
            if(sel){
              selAddNs=info.namespace; selAddId=info.id; selAddLabel=info.label;
            }else{
              selAddNs=""; selAddId=""; selAddLabel="";
            }
            ds.find(".selection-add-id").val(selAddId);
            ds.find(".selection-add-label").val(selAddLabel);
            selAdd.find(".selection-add-id").text(selAddId);
            selAdd.find(".selection-add-label").text(selAddLabel);
          }
          onJson = function(json){
            // OK now build the select-option
            var o = buildSelectList(json, {}, getJson, onSelection);
            ds.after(o);
            //o.after(selAdd);
          }
          jsonUrl=ds.find(".json-data-source-url").val();
          if(jsonUrl){
            json=getJson(jsonUrl, true, onJson);
            if(/\//.test(jsonUrl)){
              jsonUrl=jsonUrl.split(/\/([^\/]*$)/)[0]+"/";  // split at the last /
            }else{
              jsonUrl="";
            }
          }else{
            json=$(".json-data-source");
            json = json.val() || json.text();
            try{
              json = $.parseJSON(json);
              //json = eval("("+json+")");
              onJson(json);
            }catch(e){
              alert("Not valid json! - "+e);
              json = null;
              return;
            }
          }
      }

      function init(_ctx){
        var id;
        if(!_ctx)_ctx=$("body");
        ctx = _ctx;
        id=ctx.attr("id");
        widgets.formsById[id] = widgetForm;
        widgetForm.id=id;
        ctx.findx = function(selector){
            // find all selector(ed) elements but not ones that are in a subform
            var nsel = (","+selector).split(",").join(", ."+formClassName+" ");
            return ctx.find(selector).not(ctx.find(nsel));
        };

        // ==============
        // Simple (text) list input type
        // ==============
        ctx.findx(".input-list").each(listInput);
        // --------------
        // ==============
        // Multi-dropdown selection
        // ==============
        ctx.findx(".data-source-drop-down").each(sourceDropDown);
        // --------------
        ctxInputs = ctx.findx("input, textarea, select");

        //
        widgetForm.hasFileUpload= (ctx.findx("input[type=file]").size()>0);
        if(widgetForm.hasFileUpload){ setupFileUploader(); }
        if(widgets.validator){
            validator = widgets.validator();
            validator.setup(ctx);
            widgetForm.validator = validator;
            addListener("onSave", validator.isOkToSave);
            addListener("onSubmit", validator.isOkToSubmit);
        }
        ctx.findx(".form-fields-save").click(onSave);
        ctx.findx(".form-fields-submit").click(onSubmit);
        ctx.findx(".form-fields-restore").click(onRestore);
        ctx.findx(".form-fields-reset").click(onReset);
        widgetForm.ctx = ctx;
      }

      //widgetForm= {
        //submit:onSubmit,
        //save:onSave,
        //restore:onRestore,
        //reset:onReset,
        //addListener:addListener,
        //removeListener:removeListener,
        //removeListeners:removeListeners,
      //  end:true
        // setSaveUrl, setSubmitUrl, setResetJson, setRestoreData
      //};
      widgetForm.submit=onSubmit;
      widgetForm.save=onSave;
      widgetForm.restore=onRestore;
      widgetForm.reset=onReset;
      widgetForm.addListener=addListener;
      widgetForm.removeListener=removeListener;
      widgetForm.removeListeners=removeListeners;
      widgetForm._createFileSubmitter=createFileSubmitter;   // for testing only
      widgetForm._getFormData=getFormData;


      widgets.forms.push(widgetForm);
      if(ctx) init(ctx);
      return widgetForm;
  }
  widgets.formWidget = formWidget;



    function datepickerOnClose(dateText, inst){
        var month = $("#ui-datepicker-div .ui-datepicker-month :selected").val();
        var year = $("#ui-datepicker-div .ui-datepicker-year :selected").val();
        if(!month)month=0;
        $(this).datepicker('setDate', new Date(year, month, 1));
        $(this).blur();
    }
    function datepickerBeforeShow(input, inst){
        inst = $("#" + inst.id);
        if(inst.hasClass("dateMY") || inst.hasClass("dateYM") || inst.hasClass("dateY")){
            setTimeout(function(){
                $(".ui-datepicker-calendar").remove();
                $(".ui-datepicker-current").remove();
                $(".ui-datepicker-close").text("OK");
                if(inst.hasClass("dateY")) $(".ui-datepicker-month").remove();
            }, 10);
        }
    }

    function contentLoaded(){
        // ==============
        // Date inputs
        // ==============
        $("input.dateYMD, input.date").datepicker({
            dateFormat:"yy-mm-dd", changeMonth:true, changeYear:true, showButtonPanel:false
        });
        $('input.dateYM').datepicker({
            changeMonth: true, changeYear: true, showButtonPanel: true, dateFormat: 'yy-mm',
            onClose: datepickerOnClose,
            beforeShow:datepickerBeforeShow,
            onChangeMonthYear:function(year, month, inst){ datepickerBeforeShow(null, inst); },
            onSelect:function(dateText, inst){}
        });
        $('input.dateMMY').datepicker({
            changeMonth: true, changeYear: true, showButtonPanel: true, dateFormat: 'MM yy',
            onClose: datepickerOnClose,
            beforeShow:datepickerBeforeShow,
            onChangeMonthYear:function(year, month, inst){ datepickerBeforeShow(null, inst); },
            onSelect:function(dateText, inst){}
        });
        $('input.dateY').datepicker({
            changeMonth: false, changeYear: true, showButtonPanel: true, dateFormat: 'yy',
            onClose: datepickerOnClose,
            beforeShow:datepickerBeforeShow,
            onChangeMonthYear:function(year, month, inst){ datepickerBeforeShow(null, inst); },
            onSelect:function(dateText, inst){}
        });
        // ==============

        $("."+formClassName).each(function(c, e){
            try{
                widgets.formWidget($(e));
            }catch(e){
                alert("Error: "+e);
            }
        });
    }


    //widgets.forms=[];
    widgets.formsById={};
    widgets.messageBox = messageBox;
    widgets.changeToTabLayout = changeToTabLayout;
    widgets.contentLoaded = contentLoaded;
    widgets.validator = validator;
    widgets.formWidget = formWidget;

})(jQuery);



  //validator(ctx)
  //      setup:setup,
  //      test:function(){},
  //      isOkToSave:function(){return isOkToX("save");},
  //      isOkToSubmit:function(){return isOkToX("submit");},
  //      hideAllMessages:hideAllMessages,
  //      parseErrors:{}

  //formWidget(ctx)
//      return {
//        ctx:ctx,
//        submit:onSubmit,
//        save:onSave,
//        restore:onRestore,
//        reset:onReset,
//        getValidator:function(){return validator;},
//        addListener:addListener,
//        removeListener:removeListener,
//        removeListeners:removeListeners,
//        end:true
//        // setSaveUrl, setSubmitUrl, setResetJson, setRestoreData
//      };

