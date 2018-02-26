import sqlite3
db=sqlite3.connect('twitterDB.db')
db.execute("CREATE TABLE tweets (id INTEGER PRIMARY KEY, tweetID VARCHAR(30) NOT NULL, tweet BLOB NOT NULL, archiveID INTEGER NOT NULL, position INTEGER NOT NULL)")
db.execute("CREATE TABLE archives (id INTEGER PRIMARY KEY, name VARCHAR(30) NOT NULL, ownerID INTEGER NOT NULL)")
db.execute("CREATE TABLE archiveUsers (archiveID INTEGER NOT NULL, sharedUserID INTEGER NOT NULL)")
db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name char(30) NOT NULL, password char(30) NOT NULL)")
db.execute("INSERT INTO users (name,password) VALUES ('will','password')")
db.commit()