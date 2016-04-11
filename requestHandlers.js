var querystring = require("querystring");

function start(response) {
  console.log("Request handler 'start' was called.");

  var body = '<html>'+'<head>'+
    '<meta http-equiv="Content-Type content="text/html; '+
    'charset=UTF-8" />'+
    '</head>'+'<body>'+
    '소원을 입력하세요.'+'<br>'+
    '<form action="/hello" method="post">'+
    '<input type="text" name="text"></input>'+
    '<input type="submit" value="입력" />'+
    '</form>'+'</body>'+'</html>';
  response.writeHead(200, {"Content-Type" : "text/html;charset=UTF-8"});
  response.write(body);
  response.end();
}

function hello(response, postData) {
  console.log("Request handler 'hello' was called.");
  response.writeHead(200, {"Content-Type" : "text/plain;charset=UTF-8"});
  response.write("소원이 입력되었습니다. - "+ querystring.parse(postData).text);
  response.end();
}

exports.start = start;
exports.hello = hello;
