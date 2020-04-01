#!/bin/python

# rss-checker shows the newer rss feeds and prints them
# with link. Can be used for cron for email
# Author: ikwyl6@protonmail.com
#
import argparse, sys, feedparser, datetime
from time import mktime, time
import time
from Database import db

# Database credentials
dbc = "localhost", "DB-USER", "DB-PASS", "DB-NAME"
db_feed_table = "feed" # table that holds all feed urls
item_dts = [] # empty datetime object to keep oldest dt for feed.updated

def link_html(item, comment=""):
    timestamp = item[2]
    # format for what is/not given
    if timestamp != "" and not comment:
        return "- <a href=\""+item[0]+"\">"+item[1]+" ("+str(item[2])+")</a><br>"
    elif timestamp != "" and comment:
        return "- <a href=\""+item[0]+"\">"+item[1]+" ("+str(item[2])+")</a>, " + \
            "<a href=\""+comment+"\">Comments</a><br>"
    elif timestamp == "" and comment: 
        return "- <a href=\""+item[0]+"\">"+item[1]+")</a>, " + \
            "<a href=\""+comment+"\">Comments</a><br>"
    else: return "- <a href=\""+item[0]+"\">"+item[1]+"</a><br>"

# COMMAND LINE ARGUMENTS
clp = argparse.ArgumentParser(prog='rss-checker', description='check your rss feeds')
clp.add_argument('-t', '--title', help='Add feed with title')
clp.add_argument('-u', '--url', help='Add feed with url')
clp.add_argument('-o', '--output', help='Output to file')
clp.add_argument('-n', '--no-update', action='store_true', help='Do not update db time stamp for feed. Like \'dry-run\'')
clp.add_argument('-f', '--feed-id', help='Only use or check this feed id')
clp.add_argument('-l', '--list', action='store_true', help='List all Feeds')
clp.add_argument('-c', '--comments', action='store_true', help='Show link to feed comments (if available)')
clp.add_argument('--html', action='store_true', help='Output rss list in simple html')
clargs = clp.parse_args()

# If 'title' and 'url' then add the link to the db
if (clargs.title and clargs.url) or (clargs.url):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with db(dbc, db_feed_table) as db_add:
        db_add.add_feed(clargs.title, clargs.url, ts)
    exit()

# If output cmdline option is a filename
if (clargs.output):
    sys.stdout = open(clargs.output, "w")

# Create the html header for font size etc if --html used
if (clargs.html):
    print ("<html><head><style>\
            p { font-family: Arial, Helvetica, sans-serif; fone-size: small; }\
            a { text-decoration: none; }\
            a:hover { text-decoration: underline; }\
        </style></head>")

# Connect to database and get all feeds
with db(dbc, db_feed_table) as db:
    if (clargs.feed_id): db_feedlist = db.get_all_feeds(feed_id=clargs.feed_id)
    else: db_feedlist = db.get_all_feeds()
    #print (db_feedlist)
    # with each feed from db_feedlist list feeds or print the rss items
    for (db_feed_id, db_feed_title, db_feed_url, db_feed_comments, db_feed_dt) in db_feedlist:
        if (clargs.list):
            clargs.no_update = True
            print("ID: " + str(db_feed_id) + " " + db_feed_title + " (" + str(db_feed_dt) + ")")
        else:
            if (clargs.html): print(db_feed_title + "<br>")
            else: print(db_feed_title)
            item_dts.clear()
            f = feedparser.parse(db_feed_url)
            # With each rss item, convert the published date to a timestamp and
            # see if any links are newer than the db_feed_dt timestamp
            for item in f.entries:
                # See issue# 151 https://github.com/kurtmckee/feedparser/issues/151
                try:
                    item_dt = datetime.datetime.fromtimestamp(mktime(item.updated_parsed))
                except (KeyError, AttributeError, OverflowError):
                    item_dt = datetime.datetime.fromtimestamp(time.time())
                # If the rss item timestamp is greater than the feed timestamp in db
                # Add that item timestamp to the item_dts list to sort later
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
                if (clargs.html): print("No new items<br>")
                else: print("No new items")
            if (clargs.html): print("---------------------------------------------------<br>")
            else: print("---------------------------------------------------")
