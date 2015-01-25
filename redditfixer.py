import praw, random, re, sqlite3, time

USERNAME  = "SubredditLinkFixer"
PASSWORD  = "IT'S STILL A SECRET"
USERAGENT = "The SubredditLinkFixer by /u/blendt"
SUBREDDIT = "all"
MAXPOSTS = 1000000
WAIT = 60

WAITS = str(WAIT)

sql = sqlite3.connect('sql7.db')
print('Loaded SQL Database')
cur = sql.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)')
print('Loaded Completed table')

sql.commit()

r = praw.Reddit(USERAGENT)
r.login(USERNAME, PASSWORD)

def scanSub():
    print('Searching '+ SUBREDDIT + '.')
    subreddit = r.get_subreddit(SUBREDDIT)
    posts = subreddit.get_comments(limit=MAXPOSTS)
    for post in posts:
        pid = post.id
        pauthor = post.author.name

        cur.execute('SELECT * FROM oldposts WHERE ID="%s"' % pid)
        if not cur.fetchone():

            cur.execute('INSERT INTO oldposts VALUES("%s")' % pid)
            regged = re.search('((^|\s)(r|R)\/[a-zA-Z]*($|\s))', post.body.lower())
            
            if regged:
                    if post.subreddit.display_name.lower() != ("".join(regged.group(1).lower().split()))[2:] and len(("".join(regged.group(1).lower().split()))[2:]) > 1:
                        
                        post.reply("If you use both slashes like so: /" + "".join(regged.group(1).split()) + " then Reddit will automatically linkify the subreddit for you.")
                        print('Replying to ' + pid + ' by ' + pauthor)
                        print post.body.lower()
                        print "If you use both slashes like so: /" + "".join(regged.group(1).split()) + " then Reddit will automatically linkify the subreddit for you."
                        print post.subreddit.display_name.lower()
                        print ("".join(regged.group(1).lower().split()))[2:]

            regged2 = re.search('((^|\s)(u|U)\/[a-zA-Z]*($|\s))', post.body.lower())
            
            if regged2:
                    if len(("".join(regged2.group(1).lower().split()))[2:]) > 2:
                        
                        post.reply("If you use both slashes like so: /" + "".join(regged2.group(1).split()) + " then Reddit will automatically linkify the user's profile for you.")
                        print('Replying to ' + pid + ' by ' + pauthor)
                        print post.body.lower()
                        print "If you use both slashes like so: /" + "".join(regged2.group(1).split()) + " then Reddit will automatically linkify the user's profile for you."

        sql.commit

def deleteNeg():
    
    print("\nCOMMENT SCORE CHECK CYCLE STARTED")
    user = r.get_redditor(USERNAME)

    for c in user.get_comments(limit=None):
      
        if c.score < 1:
                c.delete()
                print("Comment Deleted")

      
    print("COMMENT SCORE CHECK CYCLE COMPLETED")
    print("\nComment Karma:\t\t%s"%user.comment_karma)

def unreadMessages():
    unread = 0
    for mail in r.get_unread():
            unread = unread + 1
            
    print("Unread Messages:\t" + str(unread) + "\n")

while True:
    try:
        scanSub()
        deleteNeg()
        sql.commit()
        unreadMessages()
        time.sleep(WAIT)
    except :
        print('ERROR - Running again in ' + WAITS + ' seconds \n')
        deleteNeg()
        time.sleep(WAIT)
    
