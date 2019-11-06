#!/bin/python

# rss-checker shows the newer rss feeds and prints them
# with link. Can be used for cron for email
# Author: ikwyl6@protonmail.com
#
import argparse,sys,feedparser,datetime
from time import mktime
from Database import db

# Database credentials
dbc = "localhost", "rss_checker", "rsscraigvvg", "rss_checker"
db_feed_table = "feed" # table that holds all feed urls
item_dts = [] # empty datetime object to keep oldest dt for feed.updated

def link_html(item):
    return "- <a href=\""+item[0]+"\">"+item[1]+" ("+str(item[2])+")</a><br>"

clp = argparse.ArgumentParser(prog='rss-checker', description='check your rss feeds')
clp.add_argument('-t', '--title', help='Add feed with title')
clp.add_argument('-u', '--url', help='Add feed with url')
clp.add_argument('-o', '--output', help='Output to file')
clp.add_argument('-n', '--no-update', action='store_true', help='Do not update db time stamp for feed')
clp.add_argument('-f', '--feed-id', help='Only use or check this feed id')
clp.add_argument('-l', '--list', action='store_true', help='List all Feeds')
clp.add_argument('--html', action='store_true', help='Output rss list in simple html')
clargs = clp.parse_args()

#print (clargs)

# If output cmdline option is a filename
if (clargs.output):
    sys.stdout = open (clargs.output, "w")

# Connect to database and get all feeds
with db(dbc, db_feed_table) as db:
    if (clargs.feed_id): db_feedlist = db.get_all_feeds(feed_id=clargs.feed_id)
    else: db_feedlist = db.get_all_feeds()
    #print (db_feedlist)
    # with each feed, list feeds or print the rss items 
    for (db_feed_id,db_feed_title,db_feed_url,db_feed_comments,db_feed_dt) in db_feedlist:
        if (clargs.list):
            clargs.no_update=True
            print ("ID: " + str(db_feed_id) + " " + db_feed_title + " (" + str(db_feed_dt) + ")")
        else:                
            #print ("---------------------------------------------------")
            print ("Feed: " + db_feed_title + ", " + db_feed_url) 
            item_dts.clear()
            f = feedparser.parse(db_feed_url)
            # With each rss item, convert the published date to a ts and 
            # see if any links are newer than the last time 
            for item in f.entries:
                item_dt = datetime.datetime.fromtimestamp(mktime(item.published_parsed))
                if (item_dt > db_feed_dt):
                    if (clargs.html): print (link_html((item.link,item.title,item_dt)))
                    else: 
                        print ("  -" + item.title + "\n   " + item.link + " (" + str(item_dt) + ")\n")
                        #print ("  -{:30.30}, {} ({:19})".format(str(item.title), item.link, str(item_dt))) 
                    item_dts.append(item_dt) # list of datetime stamps to update the feed.updated field
                    item_list = [item.title, item.link, item_dt]
                # item_dts may be empty if no new rss items
                try:
                    max_dt = max(item_dts) 
                    if (not clargs.no_update): db.update_feed_dt(db_feed_id, max_dt)
                except ValueError:
                    print ("No new items")
            print ("---------------------------------------------------")
     
