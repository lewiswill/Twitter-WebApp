<html>

<head>
<style type="text/css">
   body { font-family:verdana }
   form { border:solid 1px #888;width:300px; padding:100px; 
		  background-color: rgba(24,80,102,0.81);
		  margin:auto; margin-top:100px;}
   ul { list-style-type:none; padding-left:0px }
   ul li { line-height:2.5em; }
   ul li span { float:left; width:80px; text-align:right; margin-right:8px; }
   input { width:150; background-color:#fff0ff }   
   .heading { text-align:center; font-weight:bold; }
   #homeImage {width:50%; padding-left:75px; }
</style>
</head>

<body>

<form method="POST" action="{{post}}">
<div class = 'heading'>LewisTweetyPy</div>
<div><img id = 'homeImage' src='https://wallpapercave.com/wp/ave42aI.jpg'></div>
<div id = 'message'>{{message}}</div>
<ul>
<li><span>Name</span> <input name="name" type="text"></li>
<li><span>Password</span><input name="password" type="password"></li>
<li id = "buttonHolder"><span>&nbsp;</span><input type="submit"></li>
</ul>
<div id="link">
    <a href="{{link}}">{{linkMessage}}</a>
</div>
</form>
			  
</body>
</html