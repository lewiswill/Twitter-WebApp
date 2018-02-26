from bottle import route, request, debug, run, template, redirect
import urllib2
import twurl
import json
import sqlite3
import pickle
from operator import itemgetter

session = { 'archiveID' : 1, 'userInfo': []}

def makeMenu():
    global session
    menu = "<h1 id ='homeH1'>LewisTweetyPy</h1>"
    menu += "<img class = 'homeImg' src='https://wallpapercave.com/wp/ave42aI.jpg'><br>"
    menu += "<a id = 'logout' href='/logout' title='Logout'><i class='fa fa-sign-out' aria-hidden='true'></i>Logout</a>"
    menu += "<h4 class = 'menuTitle'>Current User:</h4>"
    menu += "<ul style='list-style: none;'><li class><a id='timeline' href='/'>" + str(session['userInfo'][1]) + "'s Timeline </a></li></ul><br>"
    menu += "<h4 class = 'menuTitle'>Archives:</h4>"
    
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()   
    # Retrieves all archives
    archives = getArchives()
    menu += "<ul style='list-style: none;'>"
    for i in archives:
    	cursor.execute("select tweet from tweets where archiveID=?", (i[0],))
    	result = cursor.fetchall()
        menu += "<li><a href='/showArchive/" + str(i[0]) + "'>" + \
        i[1] + " (" + str(
            len(result)) + ")</a></li><br>"
    menu += "</ul>"
    menu += "<h4 class = 'menuTitle'>Shared Archives:</h4>" 
    # Retrives all shared archives
    cursor.execute(
        "SELECT id, name FROM archives WHERE id=(SELECT archiveID FROM archiveUsers WHERE sharedUserID=?) "
        "ORDER BY name ASC", (str(session['userInfo'][0])))
    shared_archives = cursor.fetchall()
    menu += "<ul style='list-style: none;'>"
    for i in shared_archives:
        # Retrieves length of archive
        cursor.execute("SELECT tweet FROM tweets WHERE archiveID=?", (i[0],))
        result = cursor.fetchall()
        menu += "<li><a href='/showArchive/" + str(i[0]) + "'>" + \
                i[1] + " (" + str(
            len(result)) + ")</a></li><br>"
    menu += "</ul>"
    menu += "<h4 class = 'menuTitle'>Create a new Archive:</h4>"
    menu += '''<form class = 'createArchive' method='post' action='/addArchive'>
               <input class = 'center-align' type='text' name='newArchive' size='15' placeholder='Archive Name'><br>
               <input type='submit' name='submit' value='Create'>
               </form>'''    
    cursor.close()
    connect.close()
    return menu

def getArchives():
    global session
    # get all owners archives - names and id
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("SELECT DISTINCT archives.id, archives.name FROM archives WHERE "
                   "archives.ownerID=? ORDER BY archives.name ASC",
                   (session['userInfo'][0],))
    ownedArchives = cursor.fetchall()
    cursor.close()
    connect.close()

    return ownedArchives

def getArchiveName(count):
    global session
    # check if archive is owned by the current user
    users_owned_archive = checkForArchiveOwner(session['userInfo'][0], session['archiveID']) 
    # retrieve the current archives name
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("SELECT name FROM archives WHERE id=?", (session['archiveID'],))
    archive_name = cursor.fetchone()    
    header = "<h2 class = 'pageHeading'>Archive: " + str(archive_name[0]) + " ({}) </h2>".format(count) 
    # if user owns the archive then allow them to share it and delete it
    if users_owned_archive:
        # get all users to share archive with
        users = shareArchiveDropdown()   
        # enable owner to delete their archive
        header += "<p class = 'pageHeading'><a href='/deleteArchive'>[Delete Archive]</a></p>"
        header += users
    else:
        # display name of user who shared the archive
        archive_owner = getArchiveOwner()
        header += "<p class = 'pageHeading'>Archive was shared by: " + str(archive_owner[1]) + "</p>"
        header += "<p class = 'pageHeading'><a href='/unfollowArchive'> [Click to Unfollow Archive]</a></p>"

    cursor.close()
    connect.close()
    return header

def getArchiveOwner():
    global session
    # get all owners archives - names and id
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("SELECT id, name FROM users WHERE id=(SELECT ownerID FROM archives WHERE id=?)",
                   (session['archiveID'],))
    ownersArchive = cursor.fetchone()
    return ownersArchive

def checkForArchiveOwner(user, archiveID): 
	connect = sqlite3.connect('twitterDB.db')
	cursor = connect.cursor()
	cursor.execute("SELECT * FROM archives WHERE ownerID=? and id=?", (user, archiveID,),)
	found = cursor.fetchall()
	cursor.close()
	connect.close()

	if found:
		return found #Returns found if the current user is the archive owner
	else:
		return False

def shareArchiveDropdown():
    global session
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    #Retrieving Names and IDs of users not shared with
    cursor.execute(
        "SELECT id, name FROM users WHERE NOT EXISTS "
        "(SELECT * FROM archiveUsers WHERE archiveUsers.sharedUserID=users.id "
        "AND archiveUsers.archiveID=?) AND id != ? ORDER by users.name ASC",
        (session['archiveID'], session['userInfo'][0],))
    usersNotShared = cursor.fetchall()
    cursor.close()
    connect.close()
    #Dropdown for sharing to other users not previously shared with
    html = "<form name ='shareArchive' method='POST' action='/shareArchive'>"
    html += "<p class = 'center-align'><select name='sharedUserID' onchange='form.submit()'>"
    html += "<option>- - Share archive with - -</option>"
    for user in usersNotShared:
        html += "<option value='" + str(user[0]) + "'>" + user[1] + "</option>"
    html += "</select></form></p>"

    return html

def makeArchiveDropdown(tweetId):
    global session
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("select id, name, ownerID from archives " "where not exists(select * from tweets where tweets.tweetID=? and archives.id = archiveID) " "and ownerID=?", (tweetId, session['userInfo'][0],))
    result = cursor.fetchall()
    html = "<select name='archiveID' onchange='form.submit()'>"
    html += "<option>Save to...</option>"
    for i in result:
    	html += "<option value='" + str(i[0]) + "'>" + i[1] + "</option>"
    html += "</select>" 
    cursor.close()
    connect.close()
    return html

def callAPI(twitter_url, parameters):
    url=twurl.augment(twitter_url, parameters)
    connection = urllib2.urlopen(url)
    return connection.read()

def makeTweet(item, mode, archive_list):
    global session
    html, tweet_html, links = '', item['text'], ''
    user_mentions, hashtags, images, urls = [], [], [], []

    # Searching for @username
    if 'user_mentions' in item['entities']:
        for user in item['entities']['user_mentions']:
            user_mentions.append([user['indices'][0], user['indices'][1], 'user', user['screen_name']])

    # Searching for hashtags
    if 'hashtags' in item['entities']:
        for hashtag in item['entities']['hashtags']:
            hashtags.append(hashtag['text'])

    # Searching for images
    if 'media' in item['entities']:
        for image in item['entities']['media']:
            images.append(image['media_url'])

    # Searching for all URLS
    if 'urls' in item['entities']:
        for url in item['entities']['urls']:
            urls.append([url['url'], url['expanded_url']])

    if mode == 'myTimeline':
        links = "<form name='archive' method='post' action='/archive'>"
        links += "<input type='hidden' name='tweetID' value='" + str(item['id']) + "'>"
        links += archive_list
        links += "</form>"

    elif mode == 'archive':

        is_owner = checkForArchiveOwner(session['userInfo'][0], session['archiveID'])

        # Enables archive management IF they are the owner
        if is_owner:
            links = "<a href='/moveUp/" + str(item['id']) + "'><img class = 'archiveManage' title = 'Move Up' alt = 'Move Up' src='https://cdn3.iconfinder.com/data/icons/google-material-design-icons/48/ic_keyboard_arrow_up_48px-128.png' /></a><br>" + \
                    "<a href='/moveDown/" + str(item['id']) + "'><img class = 'archiveManage' title = 'Move Down' alt = 'Move Down' src='https://cdn3.iconfinder.com/data/icons/google-material-design-icons/48/ic_keyboard_arrow_down_48px-128.png'</a><br>" + \
                    "<a href='/deleteTweet/" + str(item['id']) + "'><img class = 'deleteTweet' title = 'Delete Tweet' alt ='Delete Tweet' src='https://cdn2.iconfinder.com/data/icons/gentle-edges-icon-set/128/Iconfinder_0041_5.png'</a>"
    else:
        return

    sorted_user_mentions = sorted(user_mentions, key=itemgetter(0))
    sorted_hashtags = sorted(hashtags, key=itemgetter(0))
    sorted_images = sorted(images, key=itemgetter(0))
    sorted_urls = sorted(urls, key=itemgetter(0))

    for user in sorted_user_mentions:
        tweet_html = tweet_html.replace("@" + user[3], "<a href='/userMentions/" + user[3] + "'>@" + user[3] + "</a>")

    for hashtag in sorted_hashtags:
        tweet_html = tweet_html.replace("#" + hashtag, "<a href='/searchHashtag/" + hashtag + "'>#" + hashtag + " </a>")

    for url in sorted_urls:
        tweet_html = tweet_html.replace(url[0], "<a target='_blank' href='" + url[1] + "'>" + url[0] + "</a>")

    for image in sorted_images:
        tweet_html += "<br><img class = 'tweetedImage' src='" + image + "'>"


    html += "<table><tr valign='top'><td width='70'>"
    html += "<img src='" + item['user']['profile_image_url'] + "'></td>"
    html += "<td id = 'userField'><a id ='userHandle' href='/userMentions/" + item['user'][
        'screen_name'] + "'>@" + item['user']['screen_name'] + "</a> (" + item['user']['name'] + ")"
    html += "</td></tr>"
    html += "<tr><td>" + links + "</td><td class='tweetField'>" + tweet_html + "<br>"
    html += "<div><i class='fa fa-retweet' aria-hidden='true'></i>"\
            + str(item['retweet_count']) + \
             "<i class='fa fa-heart' aria-hidden='true'></i>" \
            + str(item['favorite_count']) + "</div>"
    html += "</td></tr></table><hr>"

    return html

def showMyTimeline():
	twitter_url='https://api.twitter.com/1.1/statuses/home_timeline.json'
	parameters = {'count':15}
	data = callAPI(twitter_url, parameters)
	js = json.loads(data)
	html = ''
	for item in js:
		archives = makeArchiveDropdown(item['id'])
		html += makeTweet(item, 'myTimeline', archives)
	return html

def getTweet(id):#
	twitter_url='https://api.twitter.com/1.1/statuses/show.json'
	parameters = {'id':id}
	data = callAPI(twitter_url, parameters)
	return json.loads(data)

def callApi(twitter_url, parameters):#
    url = twurl.augment(twitter_url, parameters)
    connection = urllib2.urlopen(url)
    return connection.read()

def showStoredTweets(archiveID):#
	connect = sqlite3.connect('twitterDB.db')
	cursor = connect.cursor()
	cursor.execute("SELECT tweet FROM tweets WHERE archiveID=? order by position ASC", (archiveID,))
	result = cursor.fetchall()
	count = len(result)
	cursor.close()
	connect.close()
	html = ''
	for tweet in result:
		html += makeTweet(pickle.loads(tweet[0]), 'archive', '')
	return html, count


@route('/archive', method='post')
def archiveTweet():#
	global session
	archiveID = request.POST.get('archiveID', '').strip()
	tweetID = request.POST.get('tweetID', '').strip()
	pickledTweet = pickle.dumps(getTweet(tweetID))
	connect = sqlite3.connect('twitterDB.db')
	cursor = connect.cursor()
	cursor.execute("SELECT position FROM tweets WHERE archiveID=? ORDER BY position DESC LIMIT 1",
				   (archiveID,))
	dbRow = cursor.fetchone()
	if dbRow is not None:
		nextPosition = int(dbRow[0])+1
	else:
		nextPosition = 1	
	cursor.execute("INSERT INTO tweets (tweetID, tweet, archiveID, position) VALUES (?,?,?,?)", \
				  (tweetID, sqlite3.Binary(pickledTweet), archiveID, nextPosition))
	connect.commit()
	cursor.close()
	connect.close()
	session['archiveID'] = archiveID
	html, count = showStoredTweets(archiveID)
	return template('showTweets.tpl', heading=getArchiveName(count), menu=makeMenu(), html=html)


@route('/deleteTweet/<id>')
def deleteTweet(id):#
	global session
	connect = sqlite3.connect('twitterDB.db')
	cursor = connect.cursor()
	cursor.execute("DELETE from tweets WHERE tweetID=? and archiveID=?", (id,session['archiveID']))
	connect.commit()
	cursor.close()
	connect.close()
	html, count = showStoredTweets(session['archiveID'])
	return template('showTweets.tpl', heading=getArchiveName(count), menu=makeMenu(), html=html)


def searchForTweets(searchTerm):#
    twitter_url = 'https://api.twitter.com/1.1/search/tweets.json'
    url = twurl.augment(twitter_url, {'q': searchTerm, 'count': 10})
    connection = urllib2.urlopen(url)
    data = connection.read()
    js = json.loads(data)
    html = ''

    for item in js['statuses']:
        archives = makeArchiveDropdown(item['id'])
        html += makeTweet(item, 'myTimeline', archives)
    return html

@route('/userMentions/<name>')
def user_mentions(name):#
    mention = "@" + name
    html = searchForTweets(name)
    return template('showTweets.tpl', heading=name, menu=makeMenu(), html=html)

@route('/searchHashtag/<hashtag>')
def search_for_hashtag(hashtag):#
    hashtag = "#" + hashtag
    html = searchForTweets(hashtag)
    return template('showTweets.tpl', heading=hashtag, menu=makeMenu(), html=html)

@route('/showArchive/<archive_id>')
def show_archive(archive_id):#
    global session
    session['archiveID'] = archive_id
    html, count = showStoredTweets(archive_id)

    return template('showTweets.tpl', heading=getArchiveName(count), menu=makeMenu(), html=html)	

@route('/addArchive', method='post')
def addArchive():#
    global session
    newArchive = request.POST.get('newArchive', '').strip()
    if newArchive != '':
        connect = sqlite3.connect('twitterDB.db')
        cursor = connect.cursor()
        # Adding the new archive name and the owner to the database
        cursor.execute("INSERT INTO archives (name, ownerID) VALUES (?,?)", (newArchive, session['userInfo'][0],))
        connect.commit()
        cursor.close()
        connect.close()
    user = session['userInfo'][1] + '\'s'
    html = showMyTimeline()
    return template('showTweets.tpl', heading=user + " Timeline", menu=makeMenu(), html=html)

@route('/shareArchive', method='post')
def shareArchive():#
    global session
    sharedUserID = request.POST.get('sharedUserID', '').strip()
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()   
    cursor.execute("INSERT INTO archiveUsers (archiveID, sharedUserID) VALUES (?,?)",(session['archiveID'], sharedUserID))
    connect.commit()
    cursor.close()
    connect.close() 
    redirect('/showArchive/' + session['archiveID'])

@route('/deleteArchive')
def delete_archive():#
    global session
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("DELETE from archives WHERE id=?", (session['archiveID']))
    cursor.execute("DELETE from tweets WHERE archiveID=?", (session['archiveID']))
    connect.commit()
    cursor.close()
    connect.close()
    user = session['userInfo'][1] + '\'s'
    html = showMyTimeline()
    return template('showTweets.tpl', heading=user + " Timeline", menu=makeMenu(), html=html)

@route('/unfollowArchive')
def delete_archive():#
    global session
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("DELETE FROM archiveUsers WHERE sharedUserID=? AND archiveID=?", (session['userInfo'][0], session['archiveID'], ))
    connect.commit()
    cursor.close()
    connect.close()
    user = session['userInfo'][1] + '\'s'
    html = showMyTimeline()
    return template('showTweets.tpl', heading=user + " Timeline", menu=makeMenu(), html=html)

@route('/moveUp/<id>')
def moveUp(id):#
    global session
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("SELECT position FROM tweets WHERE tweetID=? and archiveID=?", (id,session['archiveID']))
    position = cursor.fetchone()[0]
    cursor.execute("SELECT tweetID, position FROM tweets WHERE position<? and archiveID=? order by position desc limit 1", (position,session['archiveID']))
    dbRow = cursor.fetchone()
    if dbRow is not None:
    	otherID, otherPosition = dbRow[0], dbRow[1]
    	cursor.execute("UPDATE tweets set position=? WHERE tweetID=? and archiveID=? ", (otherPosition,id,session['archiveID']))
    	cursor.execute("UPDATE tweets set position=? WHERE tweetID=? and archiveID=?", (position,otherID,session['archiveID']))    
    	connect.commit()
    cursor.close()
    connect.close()
    html, count = showStoredTweets(session['archiveID'])
    return template('showTweets.tpl', heading=getArchiveName(count), menu=makeMenu(), html=html)	

@route('/moveDown/<id>')
def moveDown(id):#
	global session
	connect = sqlite3.connect('twitterDB.db')
	cursor = connect.cursor()
	cursor.execute("SELECT position FROM tweets WHERE tweetID=? and archiveID=?", (id,session['archiveID']))
	position = cursor.fetchone()[0]
	cursor.execute("SELECT tweetID, position FROM tweets WHERE position>? and archiveID=? order by position ASC limit 1", (position,session['archiveID']))
	dbRow = cursor.fetchone()
	if dbRow is not None:
		otherID, otherPosition = dbRow[0], dbRow[1]
		cursor.execute("UPDATE tweets set position=? WHERE tweetID=? and archiveID=? ", (otherPosition,id,session['archiveID']))
		cursor.execute("UPDATE tweets set position=? WHERE tweetID=? and archiveID=?", (position,otherID,session['archiveID']))    
		connect.commit()
	cursor.close()
	connect.close()
	html, count = showStoredTweets(session['archiveID'])
	return template('showTweets.tpl', heading=getArchiveName(count), menu=makeMenu(), html=html)

@route('/')
def index():#
    global session
    if not session['userInfo']:
        redirect('/login')
    else:
        user = session['userInfo'][1] + '\'s'
    	html = showMyTimeline()
        return template('showTweets.tpl', heading=user + " Timeline", menu=makeMenu(), html=html)

def check_login(name, password):#
    global session
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM users WHERE name=? and password=?", (name, password))
    found = cursor.fetchone()
    cursor.close()
    connect.close()
    if found is not None:
		print found
		# user exists and password matches
		session['userInfo'] = found
		return True
    else:
        # user does not exist or password does not match
        return False

@route('/login')
def login():#
    return template('loginManager.tpl', message='', link='/register',
                    linkMessage='Click here to Register', post='/checkLogin')

@route('/logout')
def logout():#
	global session
	session['archiveID'] = ''
	session['userInfo'] = []
	redirect('/login')

@route('/checkLogin', method='post')
def login_submit():#
    global session
    name = request.forms.get('name')
    password = request.forms.get('password')
    if check_login(name, password):
        redirect('/')
    else:
        return template('loginChecker.tpl', message='Incorrect Username / Password, Please try again...',
                        link='/login', linkMessage='--> Click here to try Again <--',)

def addToDatabase(name, password):#
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    # add new user name and password to db
    cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)", (name, password,))
    connect.commit()
    cursor.close()
    connect.close()
    return template('loginChecker.tpl', message='Welcome to lewisTweetyPy!',
                    link='/login', linkMessage='--> Log in <--',)

@route('/register')
def registerUser():#
    return template('loginManager.tpl', message='Register to use LewisTweetyPy:', link='/login',
                    linkMessage='Already Registered? Log-in here', post='/checkSignUp')

@route('/checkSignUp', method='post')
def loginChecker():#
    name = request.forms.get('name')
    password = request.forms.get('password')
    if name == '' or password == '':
        return template('loginChecker.tpl', message='Tweety is not happy with the details provided!',
                        link='/register', linkMessage='--> Try Again <--',
                        image='http://www.picturesanimations.com/t/tweety/t17.gif', imageClass='failureImage')
    else:
        return addToDatabase(name, password)

debug(True)
run(reloader=True)
