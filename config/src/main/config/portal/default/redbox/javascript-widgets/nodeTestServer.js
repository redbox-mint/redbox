
// This is a simple (node.js) test server script

// Requires 'formidable' - http://github.com/felixge/node-formidable
// Requires 'json-template' - http://json-template.googlecode.com/files/json-template.js
//    Note: requires the following line added to the bottom of this file:
//          " exports.jsontemplate = jsontemplate; "
//    {key}  {.section key}..ifLike..{.or}..elseLike..{.end}  {.repeated section key}..loop..{.end}
//    @ - (current item) can be used in replace of the 'key' argument for the current 'key'

var log=console.log;
var exit=process.exit;
var sys=require("sys");
var fs=require("fs");
var path=require("path");
var http=require("http");
var url=require("url");
var formidable;
var jtemp;
var server, port=9123;
var htmlUploadForm;
try{
  formidable=require("formidable");
}catch(e){
  log("Requires 'formidable' - avaialble from: http://github.com/felixge/node-formidable");
  exit();
}
try{
  jtemp=require("json-template").jsontemplate;
}catch(e){
  log("Requires 'json-template' - avaiable from: http://json-template.googlecode.com/files/json-template.js");
  exit();
}
process.title="node.js Server";

htmlUploadForm="<form action='/upload' method='POST' enctype='multipart/form-data'>" +
" <a href='testForm.html'>Test form</a><br/>" +
" <input type='file' name='upload-file'/> <p><input type='text' name='testtext' value='testing [123]'/></p>" +
" <input type='checkbox' value='1' name='ajax'/>AJAX &#160; " +
" <input type='submit' value='upload'/>" +
"</form>" + "<form action='/upload?ajax=1' method='POST'><input type='text' name='tt' value='t'/><input type='submit' value='uploadAjax'/></form>";

function each(obj, func){ 
  for(var k in obj){ func(k, obj[k]); }
}

server=http.createServer(function(req, res){
  var urlInfo = url.parse(req.url);
  switch(urlInfo.pathname){
    case "/upload": fileUpload(req, res, urlInfo.query); break;
    case "/": htmlOutput(res, htmlUploadForm); break;
    default: serveFile(res, urlInfo.pathname); break;
  }
});
server.listen(port);
log("Serving on http://localhost:"+port+"/");
fs.mkdir("temp", 0777);

function serveFile(res, p){
  var d,e;
  p = path.basename(p);
  if(path.existsSync(p)){
    d = fs.readFileSync(p);
    e = path.extname(p);
    if(e==".htm" || e==".html"){
      res.writeHead(200, {"content-type":"text/html"});
      res.write(d);
      res.end();
    }else if(e==".js" || e==".json"){
      res.writeHead(200, {"content-type":"text/plain"});
      res.write(d);
      res.end();
    }else{
      show404(res);
    }
  }else{
    show404(res);
  }
}

function fileUpload(req, res, query){
  var html, t, ajax=/ajax\=/.test(query);
  var iform = new formidable.IncomingForm();
  iform.uploadDir = "temp";
  iform.keepExtensions = true;
  try{
    iform.parse(req, function(err, fields, files){
      if(fields.ajax) ajax=true;
      each(files, function(k, v){
        v.stats = fs.statSync(v.path);
      });
      if(ajax){
        for(var file in files){
          try{
            file=files[file];
            file.size = file.stats.size;
            delete file.stats;
          }catch(e){}
        }
        html = JSON.stringify({fields:fields, files:files, ok:true});
      }else{
        t = jtemp.Template("<div><p>File upload:</p> Fields:<pre>{fields}</pre> Files:<pre>{files}</pre><a href='/'>back</a></div>");
        html=t.expand({fields:JSON.stringify(fields), files:JSON.stringify(files), ok:true});
      }
      log(html);
      htmlOutput(res, html);
    });
  }catch(e){
    log("ERROR: "+e);
    htmlOutput(res, "<pre>"+e+"</pre>");
  }
}

function htmlOutput(res, html){
  res.writeHead(200, {"content-type":"text/html"});
  res.write(html);
  res.end();
}

function show404(res){
  res.writeHead(404, {"content-type":"text/plain"});
  res.write("Not found!");
  res.end();
}




