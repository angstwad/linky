/**
 * Created with PyCharm.
 * User: paul4611
 * Date: 4/17/13
 * Time: 2:34 PM
 * To change this template use File | Settings | File Templates.
 */

// jQuery
var strjson = JSON.stringify({ title: "something", url: "thingy" });
$.post("http://localhost:5000/user/e366c90e384fbea6772be69fd22f8573fe8b5708/send", strjson);
$.ajax({type: "POST", url: "http://localhost:5000/user/e366c90e384fbea6772be69fd22f8573fe8b5708/send", data: JSON.stringify({ title: "something", url: "thingy" }), contentType: "application/json" });

// Regular, ol' JS
var xmlhttp = new XMLHttpRequest();
xmlhttp.open("POST", "http://localhost:5000/user/e366c90e384fbea6772be69fd22f8573fe8b5708/send");
xmlhttp.setRequestHeader("Content-Type", "application/json");
xmlhttp.send(JSON.stringify({title: window.document.title, url: window.location.href}));

