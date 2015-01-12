import praw, random, re, sqlite3, time

USERNAME  = "SubredditLinkFixer"
PASSWORD  = "Wouldn'tyouliketoknow"
USERAGENT = "The SubredditLinkFixer by /u/blendt"
SUBREDDIT = "all"
MAXPOSTS = 1000000
WAIT = 60

WAITS = str(WAIT)

sql = sqlite3.connect('sql6.db')
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
                    if ("".join(regged2.group(1).lower().split()))[2:] > 2:
                        
                        post.reply("If you use both slashes like so: /" + "".join(regged2.group(1).split()) + " then Reddit will automatically linkify the user's profile for you.")
                        print('Replying to ' + pid + ' by ' + pauthor)
                        print post.body.lower()
                        print "If you use both slashes like so: /" + "".join(regged2.group(1).split()) + " then Reddit will automatically linkify the user's profile for you."

        sql.commit

def deleteNeg():
    
    print("COMMENT SCORE CHECK CYCLE STARTED")
    user = r.get_redditor(USERNAME)
    total = 0
    upvoted = 0
    unvoted = 0
    downvoted = 0

    for c in user.get_comments(limit=None):
      
        if len(str(c.score)) == 4:
            spaces = ""
        if len(str(c.score)) == 3:
            spaces = " "
        if len(str(c.score)) == 2:
            spaces = "  "
        if len(str(c.score)) == 1:
            spaces = "   "
      
        total = total + 1
        if c.score < 1:
                c.delete()
                downvoted = downvoted + 1
                print("Comment Deleted")
        elif c.score > 10:
                upvoted = upvoted + 1
        elif c.score > 1:
            upvoted = upvoted + 1
        elif c.score > 0:
            unvoted = unvoted + 1
      
    print ("")
    print("COMMENT SCORE CHECK CYCLE COMPLETED")
    urate = round(upvoted / float(total) * 100)
    nrate = round(unvoted / float(total) * 100)
    drate = round(downvoted / float(total) * 100)
    print("Upvoted:      %s\t%s\b\b %%"%(upvoted,urate))
    print("Unvoted       %s\t%s\b\b %%"%(unvoted,nrate))
    print("Total:        %s"%total)

while True:
    try:
        scanSub()
        deleteNeg()
        print('Running again in ' + WAITS + ' seconds \n')
        sql.commit()
        time.sleep(WAIT)
    except :
        print('ERROR - Running again in ' + WAITS + ' seconds \n')
        deleteNeg()
        time.sleep(WAIT)
    
