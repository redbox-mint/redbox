// ****************************************
// Alphanumeric sort for arrays, based on:
//   http://my.opera.com/GreyWyvern/blog/show.dml/1671288
//   author: Brian Huisman
//
// Modification is simply to alter the way full stop
//  are handled since we have no decimal numbers.
Array.prototype.alphanumSort = function(caseInsensitive) {
    for (var z = 0, t; t = this[z]; z++) {
        this[z] = [];
        var x = 0, y = -1, n = 0, i, j;
        while (i = (j = t.charAt(x++)).charCodeAt(0)) {
            var m = (i >=48 && i <= 57);
            if (m !== n) {
                this[z][++y] = "";
                n = m;
            }
            this[z][y] += j;
        }
    }
    this.sort(function(a, b) {
        for (var x = 0, aa, bb; (aa = a[x]) && (bb = b[x]); x++) {
            if (caseInsensitive) {
                aa = aa.toLowerCase();
                bb = bb.toLowerCase();
            }
            if (aa !== bb) {
                var c = Number(aa), d = Number(bb);
                if (c == aa && d == bb) {
                    return c - d;
                } else {
                    return (aa > bb) ? 1 : -1;
                }
            }
        }
        return a.length - b.length;
    });
    for (z = 0; z < this.length; z++) {
        this[z] = this[z].join("");
    }
}
// ****************************************

var widgets={forms:[], globalObject:this};


(function($){
  var globalObject=widgets.globalObject;
  var formClassName="widget-form";

  if(!$.fn.dataset){     // if dataset function not defined
      $.fn.dataset=function(name, value){return this.attr("data-"+name, value);};
  }
  if(!$.fn.getDatasets){
      $.fn.getDatasets=function(ff){
          var atts, d={}, item, name, value;
          if(this[0]){
            atts=this[0].attributes;
            for(var i=0,l=atts.length; i<l; i++){
                item=atts.item(i);
                name=item.name;
                if(name.substr(0,5)=="data-"){
                    name=name.substr(5);
                    value=item.value;
                    if(!ff || ff(name, value)){
                        d[name]=value;
                    }
                }
            }
          }
          return d;
      };
  }

  // Add these functions if not already defined (in jQuery 1.4.x)
  if(!$.fn.first){
      $.fn.first=function(){return this.eq(0);};
  }
  if(!$.fn.last){
      $.fn.last=function(){return this.eq(this.length-1);};
  }
  if(!$.isEmptyObject){
      $.isEmptyObject=function(a){for(var b in a){return false;}return true;};
  }
  if(/[native code]/.test($.fn.toString)){
      $.fn.toString=function(){return "[jQuery object("+this.size()+")]"};
  }

  function fn(s){ // inline function generator
      // fn("a,b->a+b")(3, 2)   or fn("$1+$2")(3, 2)
      var a, b, re=/^([\w$,\s]+)-\>/, re2=/;|([^\s\=]\s*\{)/;
      if(re.test(s)){
          b=s.replace(re, function(_, a1){a=a1;return "";});
      }else{
          a="$1,$2,$3,$4";
          b=s;
      }
      if(!re2.test(b)) b="return "+b;
      return new Function(a, b);
  };
  _fn = fn;

  function log(type, msg){
      if(globalObject.console){
          try{ globalObject.console[type](msg); }catch(e){}
      }
  }
  function logInfo(msg){ log("info", msg); }
  function logError(msg){ log("error", msg); }
  function logWarning(msg){ log("warn", msg); }
  function logDebug(msg){ log("debug", msg); }

  var _idNum=1;
  function getIdNum(){
      return _idNum++;
  };

  function trim(s){
    return $.trim(s);
    return s.replace(/^\s+|\s+$/g, "")
  };

  function keys(d, f){
    var keys=[], k;
    for(k in d){
        if(!f || f(k)){
            keys.push(k);
        }
    }
    return keys;
  };
  function values(d){
      var values=[], k;
      for(k in d){values.push(d[k]);}
      return values;
  };

  function getById(id){
    var e=document.getElementById(id);
    if(e){
        return $(e);
    }else{
        return $("#_doesNotExist_.-_");
    }
  };

  function reduce(c, func, i){
    if(!i)i=0;
    $.each(c, function(k, v){
      i = func(v, i);
    });
    return i;
  };

  function any(c, func){
    var k;
    for(k in c){
        if(func(k, c[k])) return true;
    }
    return false;
  };

  function isFunction(func){
      return typeof(func)==="function";
  };

  function callIfFunction(func, a, b, c){
      if($.isFunction(func)){
          try{ return func(a, b, c); }catch(e){}
      }
  };

  function messageBox(msg, cb, title){
      var msgBox=messageBox.msgBox;
      if(msgBox){msgBox.html(""); msgBox.remove(); msgBox=null;}
      if(!msgBox){  // setup
          var div, i;
          msgBox = $("<div class='box hidden' style='text-align:center;'/>");
          msgBox.append($("<span/>"));
          div = $("<div style='padding-top:1em;''/>");
          msgBox.append(div);
          i = $("<input type='button' value='OK'/>");
          div.append(i);
          messageBox.msgBox=msgBox;
          i.click(function(){
              msgBox.dialog("close");
              if($.isFunction(cb)){cb();}else{title=cb;}
          });
          msgBox.dialog({title:title||"Message", hide:"blind",
                modal:true, autoOpen:false });
      }
      msgBox.show();
      msgBox.dialog("open").find("span:first").text(msg);
  };
  _gMessageBox=messageBox;

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
  };

  function validator(){
    var iterReader, isOkToX, testTest, getExpr, getWhen;
    var hideAllMessages, setup;
    var onValidationListeners=[];
/*
(                                           1
  \s*                                           any white spaces
  (\w+)                                     2   name (word)
  \s*                                           any white spaces
  (                                         3
    \(                                          (
    (                                       4
      (                                     5
        ( ' ( [^'\\] | \\. )* ' )               'str\e'  6&7
        |
        ( " ( [^"\\] | \\. )* " )               "str\e"  8&9
        |
        ( \/ ( [^\/\\] | \\. )* \/ )            /reg\e/  10&11
        |
        (                                   12
          ( [^'"\)\(\/\\] | \\. )*              anything but ' " ) ( \ /  13
        )
        |
        (?: \( [^\)]* \) )                      do not capture ( ... )
      )*
    )
    \)                                          )
  )
  \s*
  (; | $)                                   14  ; or end of string
  \s*
)
|
(                                           15
  \s* ( ; | $ )                             16
)
 */
    //var reg1=/(\s*(\w+)\s*(\(((('([^'\\]|\\.)*')|("([^"\\]|\\.)*")|(\/([^\/\\]|\\.)*\/)|(([^'"\/\\]|\\.)*?))*?)\))\s*(;|$)\s*)|(\s*(;|$))/g; // 2, 4, 14, 15=Err
    //var reg2=/(\()|(\))|('([^'\\]|\\.)*')|("([^"\\]|\\.)*")|(\/([^\/\\]|\\.)*\/)|(\w[\w\d\._]*)|(([^\(\)\w\s'"\/\\]|\\.)+)/g;
    //var reg3=/(\s*(rule)\s*(\{((('([^'\\]|\\.)*')|("([^"\\]|\\.)*")|(\/([^\/\\]|\\.)*\/)|(([^'"\/\\]|\\.)*?))*?)\}))/g; // 4
    var reg1=/(\s*(\w+)\s*(\(((('([^'\\]|\\.)*')|("([^"\\]|\\.)*")|(\/([^\/\\]|\\.)*\/)|(([^'"\)\(\/\\]|\\.)*)|(?:\([^\)]*\)))*)\))\s*(;|$)\s*)|(\s*(;|$))/g; // 2, 4, 14, 15=Err
    var reg2=/(\()|(\))|('([^'\\]|\\.)*')|("([^"\\]|\\.)*")|(\/([^\/\\]|\\.)*\/)|(\w[\w\d\._]*)|(([^\(\)\w\s'"\/\\]|\\.)+)/g;
    var reg3=/(\s*(rule)\s*(\{((('([^'\\]|\\.)*')|("([^"\\]|\\.)*")|(\/([^\/\\]|\\.)*\/)|(([^'"\)\(\/\\]|\\.)*))*)\}))/g; // 4
    var allTests=[], actionTests={}, namedTests={};
    var results={};
    iterReader=function(arr){
      var pos=-1; l=arr.length;
      function current(){ return arr[pos]; }
      function next(){pos+=1; return current();}
      function hasMore(){return (pos+1)<l;}
      function lookAHead(){return arr[pos+1];}
      return {current:current, next:next, hasMore:hasMore, lookAHead:lookAHead};
    };
    isOkToX=function(x){
      var e=false, r;
      hideAllMessages();
      results[x]=[];
      $.each(actionTests[x]||[], function(c,f){
        r=f();
        if(!!r){results[x].push(f);}
        e|=r;
      });
      return !e;
    };
    hideAllMessages=function(){$(".validation-err-msg").hide();};
    testTest=function(name){            // run a test
        var test=namedTests[name];
        if(test && test._testFunc){
            try{
                return !test._testFunc();
            }catch(e){
            }
        }
        return false;
    };
    getExpr=function(reader){           // get a complete test expression string
      // tests: !=str, =str, /regex/, !/regex/, empty, notEmpty, email, date, [>1], (), ex1 AND ex2, ex1 OR ex2,
      var v=reader.next(), expr="", getNumber;
      var vl=v.toLowerCase();
      getNumber=function(){
          var v, n = NaN;
          v=reader.next();
          if(v=="("){v=reader.next();if(reader.lookAHead()==")")reader.next();}
          return v*1;
      }
      // macros
      if(vl=="email"){v="/.+?\\@.+\\..+?/";}
      else if(vl=="yyyy"){    v="/^[12]\\d{3}$/";}
      else if(vl=="yyyymm"){  v="/^[12]\\d{3}([\\/\\\\\\-](0?[1-9]|1[012])|((0[1-9])|(1[012])))$/";}
      else if(vl=="yyyymmdd"){v="/^[12]\\d{3}([\\/\\\\\\-](0?[1-9]|1[012])|((0[1-9])|(1[012])))([\\/\\\\\\-](0?[1-9]|[12]\\d|3[01])|((0[1-9])|[12]\\d|(3[01])))$/";}
      else if(vl=="yyyy_mm_dd"){v="/^[12]\\d{3}([\\/\\\\\\-](0?[1-9]|1[012]))([\\/\\\\\\-](0?[1-9]|[12]\\d|3[01]))$/";}
      else if(vl=="leneq" || vl=="lengtheq"){
          var n = getNumber();
          if(isNaN(n)){
             // Error
             return "";
          }
          v="/^.{"+n+"}$/"; }
      else if(vl=="lengt" || vl=="lengthgt"){
          var n = getNumber();
          if(isNaN(n)){
            // Error
            return "";
          }
          v="/^.{"+(n+1)+",}$/"; }
      else if(vl=="lenlt" || vl=="lengthlt"){
          var n = getNumber();
          if(isNaN(n)){
            // Error
            return "";
          }
          v="/^.{0,"+(n-1)+"}$/"; }
      //
      if(vl=="empty"){expr="(v=='')";}
      else if(vl=="notempty"){expr="(v!='')";}
      else if(vl=="checked"){expr='target.attr("checked")';}
      else if(vl=="notchecked"){expr='!target.attr("checked")';}
      else if(v=="="){expr="(v=="+reader.next()+")";}
      else if(v=="!="){expr="(v!="+reader.next()+")";}
      else if(v.charAt(0)=="/"){expr="("+v+".test(v))";}
      else if(v.substr(0,2)=="!/"){expr="("+v+".test(v))";}
      else if(v=="("){expr+="("+getExpr(reader)+")";if(reader.next()!=")"){alert("expected a ')'!");}; }
      else if(v.toLowerCase()=="not"){expr+="!"+getExpr(reader);}
      else if(/^[\w\d\._]+$/.test(v)){expr+="testTest('"+v+"')";}
      else {alert("failed to match! vl="+vl+",v="+v+",expr="+expr);}
      v=reader.lookAHead();
      if(v){
        v=v.toUpperCase();
        if(v=="AND"){reader.next(); expr+="&&"+getExpr(reader);}
        else if(v=="OR"){reader.next(); expr+="||"+getExpr(reader);}
      }
      return expr;
    };
    getWhen=function(reader){               // get a signal when(/action) & target
        var d, action, target;
        if(!reader.hasMore()) return null;
        d=reader.next();
        while(d=="," || d==";")d=reader.next();
        if(!d) return null;
        if(d.charAt(0)=="'" || d.charAt(0)=='"'){
            target=$(eval(d));
            if(reader.lookAHead()=="."){reader.next();d=reader.next();}
            else{
                return {};
                // ERROR
            }
        }
        action = d.toLowerCase();
        if(action.substr(0,2)=="on")action=action.substr(2);
        while(reader.hasMore()){
            // read upto the next , or ;
            d=reader.next();
            if(d=="," || d==";") break;
        }
        return {action:action, target:target};
    };
    setup=function(ctx){
        var rule, match, onValidation;
        var m, w, va, f, a, lf, addValidationFor;
        var validationsFor={}, liveValidationsFor={};
        //var matchQuotedStr = '("([^"\\]|\\.)*")';     // continues matching until closing (unescaped) quote
        var vLabels=ctx.find(".validation-err-msg, label[data-rule],label[data-validation-rule]");
        vLabels.hide();
        //value="for('dc:title');test(notEmpty);when(onChange)"
        addValidationFor=function(f, dict){
            a=validationsFor[f]||(validationsFor[f]=[]);
            a.push(dict);
        }
        rule=function(r){
            var dict, reader, l, lfc;
            dict={};
            match=function(){
                m=arguments;     //2, 4, 14, 15=Err
                if(m[0].length==0)return "";
                if(m[15]){
                    alert("Error: '"+m[15]+"' in '"+r+"'");
                    return "";
                }
                w=m[2].toLowerCase();
                va=m[4];
                dict[w]=va;
                return "";
            };
            r.replace(reg1, match);
            //
            lf=dict.livefor;
            if(lf){
                liveValidationsFor[lf]=dict;
                dict["for"]=null;
            }
            f=dict["for"];
            if(f){
                addValidationFor(f, dict);
            }
            if(dict["name"]){
                namedTests[dict["name"]]=dict;
            }
            if(dict.test){
              reader = iterReader(dict.test.match(reg2));
              dict.testStr = getExpr(reader);
            }
            dict.when=(dict.when||"");
            dict.whenList=[];
            m = dict.when.match(reg2);
            if(m){
                reader = iterReader(m);
                while(!!(w=getWhen(reader))){
                    dict.whenList.push(w);      // w.action & w.target
                }
            }
            allTests.push(dict);
            return dict;
        };
        vLabels.each(function(c, v){
            var r, dict;
            v=$(v);
            r = v.dataset("rule")||v.dataset("validation-rule");
            if(r){
                dict=rule(r);
                dict.label=v;
                if(!dict["for"] && !dict.livefor){
                    f=v.attr("for");
                    if(f){
                        dict["for"]=f;
                        addValidationFor(f, dict);
                    }
                }
            }
        });
        ctx.find(".validation-rule").each(function(c, v){
            var dict;
            v = $(v).val() || $(v).text();
            dict=rule(v);
        });
        ctx.find(".validation-rules").each(function(c, v){
            v = $(v).text();
            v.replace(reg3, function(){
                var v=arguments[4]; // from reg3 match
                if(v)rule(v);
            });
        });
        ctx.find("input[data-validation-rule], textarea[data-validation-rule]").each(function(c, v){
            var r, dict;
            r =$(v).dataset("validation-rule");
            if(!/;$/)r+=";";
            r +="for("+v.id+");"
            dict=rule(r);
        });
        //
        onValidation=function(r){       // called from the validation test functions
            try{
                $.each(onValidationListeners, function(c, l){
                    try{
                        l(r);
                    }catch(e){}
                });
            }catch(e){}
        };
        $.each(validationsFor, function(f, l){
            var target, getValue, showValidationMessage;
            var func, vLabel;
            target = $(document.getElementById(f));
            vLabel=vLabels.filter("[for="+f+"]");
            getValue=function(){ return target.val(); };
            showValidationMessage=function(show, label){
                try{
                    show?vLabel.show():vLabel.hide();
                    if(label){
                        show?label.show():label.hide();
                    }
                }catch(e){}
                return show;
            };
            $.each(l, function(c, d){
                if(d.testStr){
                  try{
                    //var test;
                    //eval("test=function(v){return ("+d.testStr+")}");
                    func="func=function(){var v=$.trim(getValue());"+
                        "r=showValidationMessage(!("+d.testStr+"),d.label);"+
                        "onValidation(r); return r;};";
                    eval(func);
                    func.x=d;
                    d._testFunc=func;
                    d.getValue=getValue;
                    d.target=target;
                    d.showValidationMessage=showValidationMessage;
                    d.vLabel=vLabel;
                  } catch(e){
                    alert(e.message + ", for="+d["for"]+"\nfunc="+func);
                  }
                  $.each(d.whenList, function(c, w){
                      w.target = w.target||target;
                      if(w.action){
                        w.target.bind(w.action, function(){func();return true;});
                        actionTests[w.action]||(actionTests[w.action]=[]);
                        actionTests[w.action].push(func);
                      }
                  });
                }
            });
        });
        $.each(liveValidationsFor, function(lf, dict){
            var target, testFunc, liveResult, label, t="";
            if(dict.testStr){
              try{
                target = ctx.find(lf);
                label=dict.label;
                if(label){
                    t="r?label.show():label.hide();"
                }
                testFunc = "testFunc=function(){var r,e,zid,v;"+
                    "v=$.trim($(this).val());"+
                    "if(/\\.0(\\.|$)/.test(this.id))return false;"+   // do not validate inputs with an id containing .0.
                    "r=!("+dict.testStr+");"+
                    "liveResult|=r;"+
                    "e=ctx.find('.validation-err-msg, label[data-rule],label[data-validation-rule]');"+
                    "zid=this.id.replace(/\\.\\d+(?=\\.|$)/g,'.0');"+
                    "e=e.filter('[for='+this.id+'],[for='+zid+']');"+
                    "r?e.show():e.hide();"+t+                 // r==show
                    "onValidation(r); return r;}";
                if(dict.jstest){
                    testFunc="testFunc=function(){var r=false,id=this.id,e,zid,v,t,jQ=$;"+
                    "if(/\\.0(\\.|$)/.test(id))return false;"+   // do not validate inputs with an id containing .0.
                    dict.jstest+";"+
                    "liveResult|=r;"+
                    "e=ctx.find('.validation-err-msg, label[data-rule],label[data-validation-rule]');"+
                    "zid=id.replace(/\\.\\d+(?=\\.|$)/g,'.0');"+
                    "e=e.filter('[for='+id+'],[for='+zid+']');"+
                    "r?e.show():e.hide();"+t+                 // r==show
                    "onValidation(r); return r;}";
                }
                eval(testFunc);
                testFunc.x=dict;
                dict._testFunc=testFunc;
                dict.target=target;
              } catch(e){
                alert(e + ", testFunc="+testFunc);
              }
              $.each(dict.whenList, function(c, w){
                  if(w.action){
                      // ignore w.target for now
                      target.live(w.action, testFunc);
                      actionTests[w.action]||(actionTests[w.action]=[]);
                      actionTests[w.action].push(function(){
                          liveResult=false;
                          ctx.find(lf).trigger(w.action);
                          return liveResult;
                      });
                  }
              });
            }
        });
    };
    return {
      setup:setup,
      test:function(){},
      isOkToSave:function(){return isOkToX("save");},
      isOkToSubmit:function(){return isOkToX("submit");},
      allTests:allTests,
      actionTests:actionTests,
      namedTests:namedTests,
      results:results,
      hideAllMessages:hideAllMessages,
      onValidationListeners:onValidationListeners,
      parseErrors:{}
    };
  };

  function helpWidget(e){
    var helpContent, showText, hideText, url, p, t;
    var showLink, hideLink, doNext;
    var show, hide;
    var helpContentId = e.dataset("help-content-id");
    if(helpContentId){
        helpContent = $("#" + helpContentId.replace(/(:|\.)/g,'\\$1'));
    }else{
        helpContent = e.dataset("help-content-class");
        p=e.parent();
        while(p.size()){
            t=p.find("."+helpContent);
            if(t.size()){helpContent=t; break;}
            p=p.parent();
        }
        if(!p.size()){alert("help-content-class '"+helpContent+"' not found!"); return;}
    }
    helpContent.hide();
    url=e.dataset("help-content-url");
    showLink = e.dataset("show-text") || e.find(".helpWidget-show")["0"];
    hideLink = e.dataset("hide-text") || e.find(".helpWidget-hide")["0"];
    //##
    show=function(){
        if($.trim(helpContent.text())=="" && url){
            helpContent.text("Loading help. Please wait...");
            helpContent.load(url);
        }
        helpContent.hasClass("inline")?helpContent.fadeIn():helpContent.slideDown();
        if(hideLink)e.html(hideLink);
        doNext=hide;
    };
    hide=function(){
        helpContent.hasClass("inline")?helpContent.fadeOut():helpContent.slideUp();
        if(showLink)e.html(showLink);
        doNext=show;
    };
    if(showLink)e.html(showLink);
    doNext=show;
    e.click(function(){
        _doNext=doNext;
        _helpContent=helpContent;
        doNext();
    });
  }

  function showHideCheck(e){
    var s, t, p=e;
    try{
        s=e.dataset("target-nearest-selector");
        // find the nearest matching element
        while(p[0].tagName!="BODY" && p.size()){
            t = p.find(s);
            if(t.size()){
                t.toggle(e.attr("checked"));
                e.change(function(){
                    t.toggle(e.attr("checked"));
                });
                e.click(function(){     // required for IE7
                    t.toggle(e.attr("checked"));
                });
                break;
            }
            p = p.parent();
        }
    }catch(e){
        alert("Error in showHideCheck() - "+e.message);
    }
  }

  function listInput(c, i){
    try{
      var liSect, count, tmp, visibleItems, displayRowTemplate, displaySelector;
      var add, del, getDelFuncFor, reorder, addUniqueOnly=false, resetOnAdd=false;
      var maxSize, minSize, addButton, addButtonDisableTest;
      var xfind, regFirst0, regLast;
      regFirst0 = /\.0(?=\.|$)/;
      // find a .digit. that is not followed by a .digit. -- not followed= (?!.*\.\d+(?=(\.|$)))
      regLast = /\.\d+(?=(\.|$))(?!.*\.\d+(?=(\.|$)))/;
      liSect = $(i);
      xfind = function(selector){
        // find all selector(ed) elements but not ones that are in a sub '.input-list'
        // return liSect.find(selector);
        return liSect.find(selector).not(liSect.find(".input-list").find(selector));
      };
      maxSize = liSect.dataset("max-size")*1;
      if(isNaN(maxSize)){
          maxSize=100;
      }
      if(maxSize<1)maxSize=1;
      minSize = liSect.dataset("min-size")*1;
      if(isNaN(minSize)){
          minSize=0;
      }
      if(minSize>maxSize)minSize=maxSize;
      if(liSect.hasClass("sortable")){
        //xfind("tbody").first().sortable({
        liSect.sortable({
          items:".sortable-item",
          update:function(e, ui){ reorder(); }
        });
      }
      addButton=xfind(".add-another-item, .item-add");
      liSect[0].addButton = addButton;
      addButtonDisableTest=function(){
          visibleItems = xfind(displaySelector+".count-this");
          count = visibleItems.size();
          if(count>=maxSize){addButton.attr("disabled", true);}
      }
      addButton.bind("disableTest", addButtonDisableTest);
      del=function(e){
        e.remove();
        addButton.attr("disabled", false);
        addButton.trigger("disableTest");
        reorder();
        return false;
      }
      getDelFuncFor=function(e){
          return function(){return del(e);};
      }
      var _add=function(e, force){
      }
// check all variable names
      if(xfind(".item-display").size()){
        if(xfind(".item-input-display").size()){
          alert("Error: .input-list cannot have both 'item-display' and 'item-input-display' table row classes");
          return;
        }
        // For handling 'item-display' (where there is a separate/special row for handling the display of added items)
        //    Note: if there is an 'item-display' row then it is expected that there will also be an
        //        'item-input' row as well an 'item-add' button/link
        displaySelector = ".item-display";
        tmp=xfind(displaySelector).hide();
        displayRowTemplate=tmp.eq(0);
        contentDisable(displayRowTemplate);
        add=function(e, force){
          // get item value(s) & validate (if no validation just test for is not empty)
          var values=[];
          var test=[];
          xfind(".item-input input[type=text]").each(function(c, i){
            values[c]=[$.trim($(i).val()), i.id];
            test[c]=values[c][0];
            if($(i).parents(".data-source-drop-down").size()==0)$(i).val("");   // reset
          }).eq(0).focus();
          //
          tmp = displayRowTemplate.clone().show().addClass("count-this");
          visibleItems = xfind(displaySelector+".count-this");
          if(!force){
              if(!any(values, function(_, v){ return v[0]!==""; })) return;
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
          count = visibleItems.size()+1;
          tmp.find("*[id]").each(function(c, i){
              i.id = i.id.replace(regFirst0, "."+count);
          });
          tmp.find(".item-display-item").each(function(c, i){
            var id = values[c][1].replace(regFirst0, "."+count);
            $(i).append("<input type='text' id='"+id+"' value='"+values[c][0]+
                        "' readonly='readonly' size='40' />");
          });
          tmp.find(".sort-number").text(count);
          xfind(displaySelector).last().after(tmp);
          visibleItems.find(".delete-item").show();
          tmp.find(".delete-item").click(getDelFuncFor(tmp));
          addButton.trigger("disableTest");
          if(count>=maxSize){addButton.attr("disabled", true);}
          contentSetup(tmp);
          if(resetOnAdd){
              xfind("select:first").val("").change();
          }
        }
        addButton.click(add);
        addButton[0].forceAdd = function(){add(null, true);};
        addButton[0].add = add;
        addUniqueOnly = addButton.hasClass("add-unique-only");
        resetOnAdd = addButton.hasClass("reset-on-add");
        xfind(".item-input input[type=text]").last().keypress(function(e){
          if(e.which==13){
            add();
          }
        });
      }else if(xfind(".item-input-display").size()){
        // For handling 'item-input-display' type lists
        //   Note: if there is an 'item-input-display' row then it is also excepted that there
        //      will be an 'add-another-item' button or link
        displaySelector=".item-input-display";
        if(minSize==0)minSize=1;
        tmp=xfind(displaySelector).hide();
        displayRowTemplate=tmp.eq(0);
        contentDisable(displayRowTemplate);
        add=function(){
          // NOTE: IE8 & jQuery 1.4.2 .clone(true) - causes stack overflow!
          tmp = displayRowTemplate.clone(false).show().addClass("count-this");
          visibleItems = xfind(displaySelector+".count-this");
          count = visibleItems.size()+1;
          tmp.find("*[id]").each(function(c, i){
              //$(i).addClass(i.id);
              i.id = i.id.replace(regFirst0, "."+count);
          });
          tmp.find("label[for]").each(function(c, i){
              i=$(i);
              i.attr("for", i.attr("for").replace(regFirst0, "."+count));
          });
          tmp.find(".sort-number").text(count);
          xfind(displaySelector).last().after(tmp);
          if(count<=minSize){tmp.find(".delete-item").hide();}
          else{
              visibleItems=visibleItems.add(tmp);
              //visibleItems.find(".delete-item").show();
              visibleItems.find(".delete-item").not(visibleItems.find(".input-list .delete-item")).show();
          }
          //tmp.find(".delete-item").click(getDelFuncFor(tmp));
          tmp.find(".delete-item").not(tmp.find(".input-list .delete-item")).click(getDelFuncFor(tmp));
          if(count>=maxSize){addButton.attr("disabled", true);}
          contentSetup(tmp);
        };
        for(var x=0;x<minSize;x++){
            add();
        }
        addButton.click(add);
      }
      reorder=function(){
        var xf, regFirst = /\.\d+(?=\.|$)/;
        // reorder last digit only in our direct input-list only
        visibleItems = xfind(displaySelector+".count-this");
        if(visibleItems.filter(".item-input-display").size()<=minSize){
          xfind(".item-input-display .delete-item").hide();
        }
        visibleItems.each(function(c, i){
            i=$(i);
            xf=function(selector){
                return i.find(selector).not(i.find(".input-list").find(selector));
            }
            try{
                xf("*[id]").each(function(_, i2){
                    var labels = i.find("label[for="+i2.id+"]");
                    i2.id = i2.id.replace(regLast, "."+(c+1));
                    labels.attr("for", i2.id);
                });
                // re-number the id's of sub-input-list's too
                // HACK: this currently only supports a second level list only
                // TODO: add support for any level/depths of lists.
                i.find(".input-list *[id]").each(function(_, i2){
                    i2.id = i2.id.replace(regFirst, "."+(c+1));
                });
                xf(".sort-number").text(c+1);
            }catch(e){alert(e.message)}
        });
      };
    }catch(ee){
        alert("error in listInput() - "+ee.message);
    }
  }

  var pendingWork = {};
  var trackPendingWork = false;
  var pendingWorkAllDoneFunc = null;
  function pendingWorkStart(id){
    var workId, pendingWorkDone;
    if(trackPendingWork){
        workId = getIdNum();
        pendingWork[workId]=id;
        pendingWorkDone=function(){
            delete pendingWork[workId];
            if(pendingWorkAllDoneFunc && $.isEmptyObject(pendingWork)){
                pendingWorkAllDoneFunc();
            }
        }
    }else{ pendingWorkDone=function(){}; }
    pendingWorkDone.workId = workId;
    return pendingWorkDone;
  }

  function getJsonGetter(jsonSourceUrl, jsonStrData){
      var jsonGetter, pendingWorkDone;
      var jsonBaseUrl, jsonInitUrlId, jsonCache={}, jsonData;
      if(jsonSourceUrl){
          if(/\?/.test(jsonSourceUrl)){
              jsonInitUrlId="";
              jsonBaseUrl=jsonSourceUrl;
          }else{
              if(/\//.test(jsonSourceUrl)){
                jsonInitUrlId=jsonSourceUrl.split(/\/(?=[^\/]*$)/)[1];
                jsonBaseUrl=jsonSourceUrl.split(/\/(?=[^\/]*$)/)[0]+"/";  // split at the last /
              }else{
                  jsonInitUrlId=jsonSourceUrl;
                  jsonBaseUrl="";
              }
          }
      }else{
          jsonBaseUrl="";
          jsonInitUrlId="";
      }
      if(jsonStrData){
          try{
              jsonData = $.parseJSON(jsonStrData);
              jsonCache=jsonData;
              jsonCache[""]=jsonData;
          }catch(e){
              alert("Not valid json! - "+e.message);
          }
      }
      // root or base json urlId is just an empty string e.g. ""
      jsonGetter = function(urlId, onJson, onError, notPending){
        var j, url, success, error;
        j=jsonCache[urlId];
        if(j){
            if(false){          // false to simulate a delay
                onJson(j);
            }else{
                pendingWorkDone = pendingWorkStart(url);
                setTimeout(function(){
                        try{
                            onJson(j);
                        }catch(e){
                            alert("-onJson error: "+e.message);
                        }
                        pendingWorkDone();
                    }, 10);
            }
            return;
        }
        if(urlId){
            url=jsonBaseUrl+urlId;
        }else{
            url=jsonBaseUrl+jsonInitUrlId;
        }
        if(!/\?/.test(url) && !/\.json$/.test(url)) url+=".json";
        if(notPending===true){
            pendingWorkDone=function(){};
        }else{
            pendingWorkDone = pendingWorkStart(url);
        }
        success=function(data){
            if(typeof(pendingWorkDone)==="undefined") { return; }
            if(!urlId){
                jsonCache=data;
            }
            try{
                onJson(data);
                jsonCache[urlId]=data;
            }catch(e){
                alert("onJson error: "+e.message+"  (for url='"+url+"')");
                //alert(onJson);
            }
            pendingWorkDone();
        };
        error=function(xhr,status,err){
            if(typeof(pendingWorkDone)==="undefined") { return; }
            if($.isFunction(onError))onError(status,err);
            pendingWorkDone();
        };
        //$.getJSON(url, success);
        $.ajax({url:url, dataType:"json", success:success, error:error, timeout:10000});
      }
      return jsonGetter;
  }
  _gjg = getJsonGetter;
  _g = {"json":[]};

  function makeSelectList(json){
      var s, o, ns=json.namespace||"", _default=json["default"], list=json.list;
      s = $("<select/>");
      if(!_default){
        s.append($("<option value=''>Please select one...</option>"));
      }
      $.each(list, function(_c, i){
        if(!i)return;
        o = $("<option/>");
        o.attr("value", ns+i.id);
        if((ns+i.id)==_default) o.attr("selected", "selected");
        o.text(i.label);
        s.append(o);
      });
      return s;
  }

  function dropDownListJson(_count, e){
    var selectId=e.id, jsonGetter, onJson, select;
    e = $(e);
    if(e.dataset("done")){ return; }
    selectId=e.dataset("id") || selectId;
    jsonGetter=getJsonGetter(e.dataset("json-source-url"),
                                e.dataset("json-data"));
    onJson=function(json){
        select=makeSelectList(json);
        if(selectId) select.attr("id", selectId);
        select.val(e.dataset("value"));
        if(!select.val()){select.val($.trim(e.text()));}
        if(!select.val()){select.val(e.val());}
        e.replaceWith(select);
    }
    jsonGetter("", onJson);
    e.dataset("done", "1");
  }

  // ==============
  // Multi-dropdown selection
  // ==============
  function buildSelectList(json, parent, jsonGetter, onSelection) {
      var s, o, children = {}, ns, selectable, loading;
      var onJson, onError, selected;
      try {
          ns = (json.namespace || "") || (parent.namespace || "");
          selectable = (json.selectable == null) ? (!!parent.selectable) : (!!json.selectable);
          s = $("<select/>");
          o = $("<option value=''>Please select one...</option>");
          s.append(o);
          selected = json.restored || json["default"];
          $.each(json.list, function(c, i) {
              if (i) {
                  var sel = !!(i.selectable != null ? i.selectable : selectable);
                  children[i.id] = {
                      url : (i.children == 1 ? i.id : i.children),
                      label : i.label,
                      id : i.id,
                      selectable : sel,
                      namespace : ns,
                      parent : parent,
                      desc: ""
                  };
                  if (i.desc != undefined) {
                      children[i.id].desc = i.desc;
                  }
                  o = $("<option/>");
                  o.attr("value", i.id);
                  if (i.id == selected) o.attr("selected", "selected");
                  o.text(i.label);
                  s.append(o);
              }
          });
      } catch(e) {
          _gjson = json;
          _gparent = parent;
          alert("Error in buildSelectList - " + e.message);
          throw e;
      }

      function onChange() {
          var id, child, j;
          id = s.val();
          child = children[id] || {parent:parent};
          if (s.nextUntil) {
              s.nextUntil(":not(select)").remove();
          } else {
              function removeSelects(s) {
                  if (s.size() == 0) return;
                  removeSelects(s.next("select"));
                  try{
                      // IE7 fixup - remove excess spaces (padding)
                      var p, n;
                      p = s.parent()[0];
                      n = p.childNodes[p.childNodes.length - 1];
                      if (n.nodeValue == false) {
                          p.removeChild(n);
                      }
                  } catch(e) {}
                  s.remove();
              }
              removeSelects(s.next("select"));
          }
          if (loading && loading.parent().size()) {
              loading.remove();
          }
          if (child.url) {
              loading = $("<span style='color:green;' title='id=" + child.url + "'> [loading&#160;please&#160;wait...] </span>");
              s.after(loading);
              onJson = function(j) {
                  //s.after(buildSelectList(j, child, jsonGetter, onSelection));
                  loading.replaceWith(buildSelectList(j, child, jsonGetter, onSelection));
                  s.after(" ");     // break point for IE7
                  onSelection(child);
              };
              onError = function(status) {
                  loading.text(" Error loading '" + child.url + "' " + status + " ");
                  loading.css("color", "red");
              };
              jsonGetter(child.url, onJson, onError);
          }
          onSelection(child);
      }
      s.change(onChange).change();
      //setTimeout(onChange, 10);
      return s;
  }

  function sourceDropDown(c, dsdd) {
      try {
          var ds = $(dsdd), id = dsdd.id, jsonUrl, jsonDataStr, jsonGetter;
          var selAdd, selAddNs, selAddId, selAddLabel, selAddDesc, addButtonDisableTest;
          var lastSelectionSelectable=false, selectId, dropDownLocation;
          var onSelection, onJson, onError, jsonDataSrc, topLevelId;
          var jsonConverterGetter;
          var listKey, idKey, labelKey, descKey, childrenKey, cmp;
          var descEnabled = false;

          if (ds.dataset("delay") > 0) {
              ds.dataset("delay", ds.dataset("delay") - 1);
              return;
          }
          if (ds.dataset("done")) {
              return;
          }

          listKey = ds.dataset("list-key");
          idKey = ds.dataset("id-key");
          labelKey = ds.dataset("label-key");
          descKey = ds.dataset("desc-key");
          childrenKey = ds.dataset("children-key");
          if (descKey != undefined) {
              descEnabled = true;
          }
          if (ds.find(".drop-down-location").size()) {
              dropDownLocation = ds.find(".drop-down-location");
          } else {
              ds.children("*:not(select)").hide();
          }

          selectId = ds.dataset("id");
          selAdd = ds.parent().find(".selection-add");
          jsonUrl = ds.dataset("json-source-url") || ds.find(".json-data-source-url").val();
          jsonDataSrc = ds.find(".json-data-source");
          jsonDataStr = ds.dataset("json-data") || jsonDataSrc.val() || jsonDataSrc.text();
          topLevelId = ds.dataset("top-level-id") || "";
          jsonGetter = getJsonGetter(jsonUrl, jsonDataStr);

          addButtonDisableTest = function() {
              if (lastSelectionSelectable == false) {
                  if (/BUTTON|INPUT/.test(selAdd[0].tagName)) {
                      selAdd.attr("disabled", true);
                  } else {
                      selAdd.hide();
                  }
              }
          };

          selAdd.bind("disableTest", addButtonDisableTest).trigger("disableTest");

          onSelection = function(info) {
              //info.namespace, info.id, info.label, info.selectable, info.parent
              while (info.selectable !== false && info.selectable !== true) {
                  if (info.parent) {
                      info = info.parent;
                  } else {
                      info.selectable=false;
                  }
              }

              lastSelectionSelectable = info.selectable;
              if (/BUTTON|INPUT/.test(selAdd[0].tagName)) {
                  selAdd.attr("disabled", lastSelectionSelectable ? "" : "disabled");
              } else {
                  lastSelectionSelectable ? selAdd.show() : selAdd.hide();
              }

              selAdd.trigger("disableTest");
              if (lastSelectionSelectable) {
                  selAddNs = info.namespace;
                  selAddId = info.id;
                  selAddLabel = info.label;
                  selAddDesc = info.desc;
              } else {
                  selAddNs = "";
                  selAddId = "";
                  selAddLabel = "";
                  selAddDesc = "";
              }

              ds.find(".selection-added-id").val(selAddId);
              ds.find(".selection-added-label").val(selAddLabel);
              ds.find(".selection-added-desc").val(selAddDesc);
              selAdd.find(".selection-added-id").text(selAddId);
              selAdd.find(".selection-added-label").text(selAddLabel);
              selAdd.find(".selection-added-desc").text(selAddDesc);
              // On screen help (may not be present
              if (selAddDesc == "") {
                  ds.find(".selection-add-more-info-holder").hide();
                  ds.find(".selection-add-more-info").html("");
              } else {
                  ds.find(".selection-add-more-info-holder").show();
                  ds.find(".selection-add-more-info").html(selAddDesc);
              }
          };

          jsonConverterGetter = jsonGetter;
          if (listKey || idKey || labelKey || childrenKey) {
              listKey = listKey || "list";
              idKey = idKey || "id";
              labelKey = labelKey || "label";
              descKey = descKey || "description";
              childrenKey = childrenKey || "children";
              cmp = fn("a, b->a.label == b.label ? 0 : (a.label > b.label ? 1 : -1)");

              jsonConverterGetter = function (urlId, onJson, onError, notPending) {
                  jsonGetter(urlId, function(j) {
                      // convert json
                      if (j.error) {
                          if ($.isFunction(onError)) {
                              onError(j.error);
                          } else {
                              alert("Error in json: " + j.error);
                          }
                          return;
                      }
                      j.list = j[listKey];
                      $.each(j.list, function(c, i) {
                          i.id = i[idKey];
                          i.label = i[labelKey];
                          if (descEnabled) {
                              i.desc = i[descKey];
                          }
                          // Is it a data type that has children normally
                          if (!$.isEmptyObject(i[childrenKey])) {
                              // And does this instance actually have any children
                              if (i[childrenKey].length != 0) {
                                  // where should the double escaping happen?
                                  i.children = escape(escape(i.id));
                              }
                          }
                      });
                      j.list.sort(cmp);
                      onJson(j);
                  }, onError, notPending);
              };
          } else {
              jsonConverterGetter = jsonGetter;
          }

          var selLocation = $("<span style='color:green;'> [loading&#160;please&#160;wait...] </span>");
          if (dropDownLocation) {
              dropDownLocation.prepend(selLocation);
          } else {
              ds.append(selLocation);
              ds.append(" "); // line break point of IE7
          }

          onJson = function(json) {
              try{
                  // inject default value if set
                  var _default = ds.dataset("default-value");
                  if (_default) {
                      json["default"] = _default;
                  }
                  json.restored = ds.find(".selection-added-id").val();
                  if (json.restored) {
                      json.restored = ($.trim(json.restored) == "") ? null : json.restored;
                  }
                  // OK now build the select-option
                  var o = buildSelectList(json, {"selectable" : 1}, jsonConverterGetter, onSelection);
                  if (selectId) {
                      o.attr("id", selectId);
                      selectId = null;
                  }
                  selLocation.replaceWith(o);
              } catch(e) {
                  alert("Error in sourceDropDown onJson function - " + e.message);
                  _gjson = json;
                  throw e;
              }
          };

          onError = function(status, err) {
              selLocation.text("Error failed to load selection data: " + status);
              selLocation.css("color", "red");
              ds.parent().find(".item-add,.selection-add").attr("disabled", "disabled");
              var retry = $("<a href='#'> retry</a>");
              selLocation.append(retry);
              retry.click(function() {
                  selLocation.html(" [loading&#160;please&#160;wait...] ").css("color", "green");
                  jsonConverterGetter(topLevelId, onJson, onError, true);
                  return false;
              });
          }

          jsonConverterGetter(topLevelId, onJson, onError, true);
          ds.find(".selection-added").hide();
          if (selAdd.dataset("add-on-click") != null) {
              var saLabel, saId, saLabelWidth, sTemp, w;
              saLabel = ds.parent().find(".selection-added-label");
              saId = ds.parent().find(".selection-added-id");
              saLabel.bind("onDataChanged", function() {
                  ds.find(".selection-added").toggle(!!saLabel.val());
                  if (dropDownLocation) {
                      dropDownLocation.toggle(!saLabel.val());
                  }
                  if (!saLabelWidth) {
                      saLabelWidth = saLabel.width();
                  }
                  if (saLabelWidth) {   // adjust width as required
                      sTemp = $("<span/>");
                      sTemp.text(saLabel.val() || "").hide().insertAfter(saLabel);
                      w = sTemp.width() + 4;
                      sTemp.remove();
                      saLabel.width(w > saLabelWidth ? w : saLabelWidth);
                  }
              }); //.trigger("onDataChanged");

              ds.parent().find(".clear-item").click(function() {
                  saId.val("").trigger("onDataChanged");
                  saLabel.val("").trigger("onDataChanged");
                  selAdd.attr("disabled", false);
                  selAdd.trigger("disableTest");
                  return false;
              });

              selAdd.click(function() {
                  saId.val(selAddId).trigger("onDataChanged");
                  saLabel.val(selAddLabel).trigger("onDataChanged");
                  selAdd.trigger("disableTest");
                  if (!saLabelWidth) {
                      saLabelWidth = saLabel.width();
                  }
                  if (saLabelWidth) {   // adjust width as required
                      sTemp = $("<span/>");
                      sTemp.text(selAddLabel).hide().insertAfter(saLabel);
                      w = sTemp.width() + 4;
                      sTemp.remove();
                      saLabel.width(w > saLabelWidth ? w : saLabelWidth);
                  }
                  return false;
              });
          }
          ds.dataset("done", 1);
      } catch(e) {
          alert("Error in sourceDropDown() - " + e.message);
      }
  }

  function formWidget(ctx, globalObject, validator){
      // functions
      var addListener, removeListener, removeListeners, raiseEvents
      var onSubmit, onSave, onRestore, onReset, hasChanges, lastData={};
      var submit, save, submitSave, getFormData, restore
      var reset, setupFileUploader, getFileUploadInfo, createFileSubmitter, init
      // variables
      var widgetForm={};
      var listeners={};
      var ctxInputs;

      addListener=function(name, func){
          var l;
          l=listeners[name];
          if(!l){
              l = [];
              listeners[name]=l;
          }
          l.push(func);
      };
      removeListener=function(name, func){
          var l, i;
          l=listeners[name]||[];
          i=$.inArray(name, l);
          if(i>-1)l.splice(i, 1);
      };
      removeListeners=function(name){
          delete listeners[name];
      };
      raiseEvents=function(name){
          var l=listeners[name]||[];
          for(var k in l){
              var f = l[k];
              try{
                  if(f(ctx)===false) return false; // cancel event
              }catch(e){}
          }
      };

      onSubmit=function(){
        if(raiseEvents("onSubmit")===false){
            return false;
        }
        submit();
        return true;
      };
      onSave=function(){
        if(raiseEvents("onSave")===false){
            return false;
        }
        save();
        return true;
      };
      onRestore=function(data){
        if(raiseEvents("preOnRestore")==false){
            return false;
        }
        //messageBox(JSON.stringify(data))
        restore(data);
        lastData = getFormData();
        raiseEvents("postOnRestore");
        return true;
      };
      onReset=function(data){
        if(raiseEvents("preOnReset")==false){
            return false;
        }
        reset(data);
        raiseEvent("postOnReset");
        return true;
      };

      hasChanges=function(){
          var cData, u, lv;
          cData=getFormData();
          return any(cData, function(k,v){
              lv=lastData[k];
              if(v===lv)return false;
              if(lv===u || v===u)return true;   // if either is undefined
              return v.toString()!=lv.toString();
          });
      };

      submit=function(){
          submitSave("submit");
      };

      save=function(){
          submitSave("save");
      };

      submitSave=function(stype){
        var data, url;
        var xPreFunc, xFunc, xResultFunc, xErrResultFunc;
        var replaceFunc, completed;
        replaceFunc=function(s){
            s = s.replace(/[{}()]/g, "");   // make it safe - no function calls
            return eval(s);
        };
        if(globalObject){
            xPreFunc = globalObject[ctx.dataset("pre-"+stype+"-func")];
            xFunc = globalObject[ctx.dataset(stype+"-func")];
            xResultFunc = globalObject[ctx.dataset(stype+"-result-func")];
            xErrResultFunc = globalObject[ctx.dataset(stype+"-err-result-func")]
        }
        if(callIfFunction(xPreFunc, widgetForm)===false){
            callIfFunction(xResultFunc, widgetForm, {error:"canceled by pre-"+stype+"-func"});
            return false;
        }
        data = getFormData();
        completed=function(data, dataStr){
            if(typeof(getFormData)==="undefined") { return; }
            if(typeof(data)=="string"){
                dataStr=data;
                try{
                    data = JSON.parse(data);
                }catch(e){
                    data = {error:e};
                }
            }
            if(data.error || !data.ok){
                ctx.findx(".saved-result").html("");
                if(callIfFunction(xErrResultFunc, widgetForm, data)!=false){
                    if(!data.ok && !data.error) data.error="Failed to receive an 'ok'!";
                    messageBox("Failed to "+stype+"! (error='"+data.error+"') response='"+dataStr+"'");
                }
            }else{
                callIfFunction(xResultFunc, widgetForm, data);
                var sr;
                if(stype=="save"){
                    sr=ctx.findx(".saved-result").text("Saved OK").
                        css("color", "green").show().fadeOut(4000);
                }else if(stype=="submit"){
                    sr=ctx.findx(".submit-result").text("Submitted OK").
                        css("color", "green").show().fadeOut(4000);
                }
                setTimeout(function(){sr.hide();}, 4100);  // work around for bug in fadeOut not hiding invisible items
                // update ctxInputs - as fileInputs will now be different
                ctxInputs=ctx.findx("input, textarea, select");
                lastData = getFormData();
            }
        };
        if(data.title===null)data.title=data["dc:title"];
        if(data.description===null)data.description=data["dc:description"];
        if(callIfFunction(xFunc, widgetForm, data)===false){
            callIfFunction(xResultFunc, widgetForm, {error:"canceled by "+stype+"-func"});
            return false;
        }
        url = ctx.dataset(stype+"-url") || ctx.findx(".form-fields-"+stype+"-url").val();
        //logInfo(stype+" url="+url);
        if(url){
            url = url.replace(/{[^}]+}/g, replaceFunc);
            if(widgetForm.hasFileUpload){
                var elems=[], h=$("<input type='text' name='json' />");
                var fileSubmitter = createFileSubmitter();
                h.val(JSON.stringify(data));
                elems.push(h[0]);
                $.each(data, function(k, v){
                    h=$("<input type='text' />");
                    h.attr("name", k); h.val(v);
                    elems.push(h[0]);
                });
                ctx.findx("input[type=file]").each(function(c, f){
                    elems.push(f);
                });
                setTimeout(function(){fileSubmitter.submit(url, elems, completed);}, 10);
            }else{
                // data.json = JSON.stringify(data);
                $.ajax({type:"POST", url:url, data:data,
                    success:completed,
                    error:function(xhr, status, e){
                        if(typeof(completed)==="undefined") { return; }
                        completed({error:"status='"+status+"'"}, xhr.responseText);
                    },
                    dataType:"json"
                });
            }
        }else{
            completed({"ok":true});
        }
      };

      getFormData=function(){
        var data={}, s, v, e, formFields;
        var getValue, getXValue;
        var regFirst0=/\.0(?=\.|$)/;
        formFields = ctx.dataset("form-fields") || ctx.findx(".form-fields").val()
        formFields += ","+ (ctx.dataset("form-fields-readonly") || ctx.findx(".form-fields-readonly").val());
        formFields = $.grep(formFields.split(/[\s,]+/),
                                function(i){return /\S/.test(i)});
        getValue=function(i){
          e = getById(i);
          if(e.size()==0) e=ctxInputs.filter("[name="+i+"]");
          if(e.size()==0){return null;}
          v = e.val();
          if(e.attr("type")==="checkbox"){
            if(!e.attr("checked")){v="";}
          } else if(e.attr("type")==="radio"){
            v = e.filter(":checked").val();
          }
          return v;
        };
        getXValue=function(i){
            var id, count=1;
            while(true){
             try{
              id = i.replace(regFirst0, "."+count);
              if(regFirst0.test(id)){
                  if(getXValue(id)==1){
                      // stop counting when x.1 does not get a value
                      return count;
                  }
              }else{
                v=getValue(id);
                if(v===null) return count;
                data[id]=v;
              }
              count+=1;
             }catch(e){
                 alert(e);
                 throw e;
             }
            }
        }
        $.each(formFields, function(c, i){
            if(/\.0+(\.|$)/.test(i)){
                getXValue(i);
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
      };

      restore=function(data){
          var keys=[], skeys=[], input, t, formFields, regAll, regLast;
          regAll = /\.\d+(?=(\.|$))/;
          // find a .digit. that is not followed by a .digit. -- not followed= (?!.*\.\d+(?=(\.|$)))
          regLast = /\.\d+(?=(\.|$))(?!.*\.\d+(?=(\.|$)))/;
          ctxInputs = ctx.findx("input, textarea, select");
          formFields = ctx.dataset("form-fields") || ctx.findx(".form-fields:first").val();
          formFields = $.grep(formFields.split(/[\s,]+/),
                                function(i){return /\S/.test(i)});
          $.each(data, function(k, v){keys.push(k);});
          keys.alphanumSort(true);
          skeys = $.grep(keys, function(i){return /\.\d+(\.|$)/.test(i);}, true);
          _gc = ctxInputs;
          $.each(skeys, function(c, v){
              if($.inArray(v, formFields)!=-1){
                  t=ctxInputs.filter("[id="+v+"]");
                  if(t.size()){
                    if(t.attr("type")!="checkbox"){
                        t.val(data[v].replace(/\\n/g,"\n")).trigger("onDataChanged");
                    }else{
                        t.attr("checked", data[v]).trigger("onDataChanged");
                    }
                  }else{
                      t=ctxInputs.filter("[type=radio][name="+v+"][value="+data[v]+"]");
                      t.attr("checked", true);
                  }
              }
          });
          // list items
          skeys = $.grep(keys, function(i){return /\.\d+(\.|$)/.test(i);});
          $.each(skeys, function(c, v){
              var k, il, addButton;
              k = v.replace(regLast, ".0");
              try{
                  if($.inArray(k.replace(regAll,".0"), formFields)!=-1){
                      input = ctxInputs.filter("[id="+v+"]");
                      if(input.size()==0){
                        input = ctxInputs.filter("[id="+k+"]");
                        il=input.parents(".input-list").first();
                        if(il.size()){
                            addButton=il[0].addButton;
                            if(addButton.size()){
                                if(addButton[0].forceAdd){
                                    addButton[0].forceAdd();
                                }else{
                                    addButton.click();
                                }
                            }
                        }
                        // update inputs - this could be done better
                        ctxInputs = ctx.findx("input, textarea, select");
                        input = ctxInputs.filter("[id="+v+"]");
                        if(input.size()==0){
                            alert("id '"+v+"' not found!");
                        }
                      }else{
                          //alert("found '"+v+"' ok");
                      }
                      if(input.attr("type")=="checkbox"){
                        input.attr("checked", !!data[v]);
                        input.change().trigger("onDataChanged");
                      }else{
                        input.val(data[v]).trigger("onDataChanged");
                      }
                  }
              }catch(e){
                  alert("Error in restore() - "+e.message);
              }
          });
      };

      reset=function(data){
          if(!data)data={};
          //
      };

      setupFileUploader=function(fileUploadSections, onChange){
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
      };

      getFileUploadInfo=function(file){
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
      };

      createFileSubmitter=function(){
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
                  // need to use the original as the clone doesn't contain
                  // the file values in browsers such as Chrome and Safari
                  var source=$(e);
                  var cloned=source.clone(true);
                  if(source.attr("name")===""){source.attr("name", e.id);}
                  cloned.insertAfter(source);
                  form.append(source);
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
      };

      init=function(_ctx, validator){
        var id, idu, notCtx;
        if(!_ctx)_ctx=$("body");
        ctx = _ctx;
        notCtx = ctx.find("."+formClassName);
        id=ctx.attr("id");
        widgetForm.id=id;
        ctx.findx=function(selector){
            // find all selector(ed) elements but not ones that are in a subform
            //var nsel=(","+selector).split(",").join(", ."+formClassName+" ");
            //return ctx.find(selector).not(ctx.find(nsel));
            return $(selector, ctx).not( $(selector, notCtx) );
        };
        ctxInputs=ctx.findx("input, textarea, select");
        //
        widgetForm.hasFileUpload= (ctx.findx("input[type=file]").size()>0);
        if(widgetForm.hasFileUpload){ setupFileUploader(); }
        if(validator){
            var v = validator();
            v.setup(ctx);
            widgetForm.validator = v;
            addListener("onSave", v.isOkToSave);
            addListener("onSubmit", v.isOkToSubmit);
        }
        ctx.findx(".form-fields-save").click(onSave);
        ctx.findx(".form-fields-submit").click(onSubmit);
        ctx.findx(".form-fields-restore").click(onRestore);
        ctx.findx(".form-fields-reset").click(onReset);
        if(ctx.dataset("on-restored")){
            addListener("postOnRestore", globalObject[ctx.dataset("post-on-restore")]);
        }
        widgetForm.ctx = ctx;
        idu=ctx.dataset("init-data-url");
        if(idu){
            $.getJSON(idu, function(j){
                if(typeof(widgetForm)==="undefined"){ return; }
                widgetForm.restore(j);
            });
        }
      };

      widgetForm.submit=onSubmit;
      widgetForm.save=onSave;
      widgetForm.restore=onRestore;
      widgetForm.reset=onReset;
      widgetForm.hasChanges=hasChanges;
      widgetForm.addListener=addListener;
      widgetForm.removeListener=removeListener;
      widgetForm.removeListeners=removeListeners;
      widgetForm._createFileSubmitter=createFileSubmitter;   // for testing only
      widgetForm._getFormData=getFormData;

      if(ctx) init(ctx, validator);
      return widgetForm;
  }


    function datepickerOnClose(dateText, inst){
        var month = $("#ui-datepicker-div .ui-datepicker-month :selected").val();
        var year = $("#ui-datepicker-div .ui-datepicker-year :selected").val();
        if(!month)month=0;
        $(this).datepicker('setDate', new Date(year, month, 1));
        $(this).blur();
    }
    function datepickerBeforeShow(input, inst){
        inst = $(inst.input);
        if(inst.hasClass("dateMY") || inst.hasClass("dateYM") || inst.hasClass("dateY")){
            setTimeout(function(){
                $(".ui-datepicker-calendar").remove();
                $(".ui-datepicker-current").remove();
                $(".ui-datepicker-close").text("OK");
                if(inst.hasClass("dateY")) $(".ui-datepicker-month").remove();
            }, 10);
        }
    }
    function contentSetup(ctx, completedCallback){
      //
      try{
        ctx.find(".helpWidget").each(function(c, e){
            helpWidget($(e));
        });
        ctx.find(".show-hide-widget").each(function(c, e){
            showHideCheck($(e));
        });
        // ==============
        // Date inputs
        // ==============
        ctx.find("input.dateYMD, input.date").datepicker({
            dateFormat:"yy-mm-dd", changeMonth:true, changeYear:true, showButtonPanel:false
        });
        ctx.find('input.dateYM').datepicker({
            changeMonth: true, changeYear: true, showButtonPanel: true, dateFormat: 'yy-mm',
            onClose: datepickerOnClose,
            beforeShow:datepickerBeforeShow,
            onChangeMonthYear:function(year, month, inst){ datepickerBeforeShow(null, inst); },
            onSelect:function(dateText, inst){}
        });
        ctx.find('input.dateMMY').datepicker({
            changeMonth: true, changeYear: true, showButtonPanel: true, dateFormat: 'MM yy',
            onClose: datepickerOnClose,
            beforeShow:datepickerBeforeShow,
            onChangeMonthYear:function(year, month, inst){ datepickerBeforeShow(null, inst); },
            onSelect:function(dateText, inst){}
        });
        ctx.find('input.dateY').datepicker({
            changeMonth: false, changeYear: true, showButtonPanel: true, dateFormat: 'yy',
            //onClose: datepickerOnClose,
            onClose: function(dateText){  // for IE7
                var year = $("#ui-datepicker-div .ui-datepicker-year :selected").val();
                $(this).val(year);
            },
            beforeShow:datepickerBeforeShow,
            onChangeMonthYear:function(year, month, inst){ datepickerBeforeShow(null, inst); },
            onSelect:function(dateText, inst){}
        });
        //
        trackPendingWork = true;
        pendingWorkAllDoneFunc=function(){
            //alert("all pending work (setup work) done!");
            trackPendingWork = false;
            // ==============
            // Simple (text) list input type
            // ==============
            ctx.find(".input-list").not(ctx.find(".input-list .input-list")).each(listInput);
            if(completedCallback){
                completedCallback();
            }
        };

        ctx.find(".drop-down-list-json").each(dropDownListJson);
        // ==============
        // Multi-dropdown selection
        // ==============
        //alert("sourceDropDown");
        ctx.find(".data-source-drop-down").each(sourceDropDown);
        if($.isEmptyObject(pendingWork)){
            // there is no pendingWork to wait for!
            pendingWorkAllDoneFunc();
        }
        gPendingWork=pendingWork;
      }catch(e){
          alert("Error in contentSetup() - "+e.message);
      }
    }

    function contentDisable(ctx){
        ctx.find("input").filter(".dateYMD, .date, .dateYM, .dateMMY, .dateY").datepicker("destroy");
    }

    function contentLoaded(completedCallback){
        //alert("contentLoaded");
        contentSetup($("body"), function(){
            $("."+formClassName).each(function(c, e){
                try{
                    var widgetForm=formWidget($(e),
                                            widgets.globalObject,
                                            widgets.validator);
                    widgets.forms.push(widgetForm);
                    widgets.formsById[widgetForm.id] = widgetForm;
                }catch(e){
                    alert("Error: "+e);
                }
            });
            if(completedCallback){
                completedCallback();
            }
        });
    }

    widgets.forms=[];
    widgets.formsById={};
    widgets.messageBox = messageBox;
    widgets.changeToTabLayout = changeToTabLayout;
    widgets.contentLoaded = contentLoaded;
    widgets.validator = validator;
    widgets.formWidget = formWidget;
})(jQuery);
