<html>
  <head>
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
  <link href="https://fonts.googleapis.com/css?family=Roboto|Roboto+Condensed" rel="stylesheet">
    <title>TweetyPy Web App</title>
    <style type='text/css'>
    body{
    font-family: 'Roboto Condensed', sans-serif;
    }
    a:hover {
    color:white;
    }
    h1{
      text-align: center;
    }
    h2{
      text-align:center;
    }
    .createArchive{
      padding-left:40px;
    }
    #menu{
          background-color: rgba(24,80,102,0.81);
         }
    #tweets{
      background-color: rgba(100,100,100,0.81);
    }
    #timeline{
      text-align: center;
    }
    .homeImg{
         width: 70%;
         padding-left:30px;
       }
    .tweetedImage{
         width: 50%;
       }
    #timelineLink{
         text align: right;
       }
       .archiveDropDown{
        display: inline-block;
        margin-left: auto;
        margin-right: auto;
        text-align: left;
       }
    .fa-heart:before {
      padding-top:10px;
      padding-left: 20px;
      color: red;
      }
    .fa-retweet:before {
      padding-top:10px;
      color: orange;
      }
    .archiveManage{
      width: 30%;
      padding-right:20px;
    }
  .deleteTweet{
    width: 20%;
  }
  .menuTitle{
    text-align:center;
  }
  #logout{
    color: orange;
    padding-top:10px;
    padding-left:70px;
  }
    </style>
  </head>
  <body>
		 <table>
		 <tr valign='top'>
		     <td id="menu" width='100'>{{!menu}}</td>
		     <td id="tweets"><h1>{{!heading}}</h1>{{!html}}</td>
		 </tr>
		 </table>   
  </body>
</html>
​
