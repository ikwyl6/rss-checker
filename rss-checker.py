#!/bin/python

# rss-checker shows the newer rss feeds and prints them
# with link. Can be used for cron for email
# Author: ikwyl6@protonmail.com
#
import argparse
import sys
import datetime
import time
from time import mktime
import feedparser
import requests
from urllib.error import URLError
from Database import db
from Database import OperationalError
import json
import os

# Database credentials
dbc = "localhost", "DB-USER", "DB-PASS", "DB-NAME"
db_feed_table = "feed"  # table that holds all feed urls
db_group_table = "groups"  # table that holds groups
config_file = os.getenv('HOME') + "/.rss_checker.json"
return_website = ('', os.getenv('RC_WEBSITE'))[os.getenv('RC_WEBSITE') != '']
item_dts = []  # empty datetime object to keep oldest dt for feed.updated
output_str = "" # used for most output to stdout/file/html


def link_html(item, comment=""):
    timestamp = item[2]
    # format for what is/not given
    if timestamp != "" and not comment:
        return "- <a href=\""+item[0]+"\">"+item[1]+" (" + str(item[2]) + \
                ")</a><br>"
    elif timestamp != "" and comment:
        return "- <a href=\""+item[0]+"\">"+item[1]+" (" + str(item[2]) + \
                ")</a>, " + \
                "<a href=\""+comment+"\">Comments</a><br>"
    elif timestamp == "" and comment:
        return "- <a href=\""+item[0]+"\">"+item[1]+")</a>, " + \
            "<a href=\""+comment+"\">Comments</a><br>"
    else:
        return "- <a href=\""+item[0]+"\">"+item[1]+"</a><br>"


# Get json options from config file items for clargs
def get_json_config(jsonfile=config_file):
    with open(jsonfile) as jf:
        data = json.load(jf)
    jf.close()
    return data


# Form the proxy info for requests Session
def get_proxy_info(**cl_kwargs):
    scheme = cl_kwargs['proxy-scheme']
    user = cl_kwargs['proxy-user']
    pw = cl_kwargs['proxy-pass']
    host = cl_kwargs['proxy-host']
    conn = cl_kwargs['proxy-conn']
    proxy = { conn : ''.join([scheme, "://", user, ":", pw, "@", host]) }
    return proxy


# COMMAND LINE ARGUMENTS
clp = argparse.ArgumentParser(prog='rss-checker', description='check your rss \
        feeds')
# Flags for ADDING FEEDS
add_group = clp.add_argument_group('ADDING FEEDS')
add_group.add_argument('-t', '--title', help='Add feed with title')
add_group.add_argument('-u', '--url', help='Add feed with url')
add_group.add_argument('--gid', type=int, help='Add feed under group gid \
        (integer). Use --list-groups to see list of groups')
add_group.add_argument('--add-group', help='Name of group to add. Use groups \
        to group your feeds together')
# Flags for USING FEEDS
use_group = clp.add_argument_group('CHECKING FEEDS')
use_group.add_argument('-a', '--all-feeds', action='store_true', help='Show all \
        feeds in output even if they don\'t have any new rss items. Default \
        is not to show them')
use_group.add_argument('-c', '--comments', action='store_true', help='Show link to \
        feed comments (if available)')
use_group.add_argument('--delete-feed', help='Delete feed using \'FEED_ID\'')
use_group.add_argument('-f', '--feed-id', help='Only use or check this feed id')
use_group.add_argument('-g', '--group', action='store_true', help='Group feeds \
        together. If used with --list, show feeds with group ids')
use_group.add_argument('--html', action='store_true', help='Output rss list in \
        simple html')
use_group.add_argument('-l', '--list', action='store_true', help='List all Feeds')
use_group.add_argument('--list-groups', action='store_true', help='List all \
        groups')
use_group.add_argument('-n', '--no-update', action='store_true', help='Do not \
        update db time stamp for each feed. Like \'dry-run\'')
use_group.add_argument('-o', '--output', help='Output to file. Default is stdout')
use_group.add_argument('-v', '--verbose', action='store_true', help='Be verbose')
use_group.add_argument('-w', '--website', dest='website' )
# Flags for using SOCKS5 PROXY
proxy_group = clp.add_argument_group("SOCKS PROXY")
proxy_group.add_argument('--proxy-user', dest='proxy_user', help='proxy user')
proxy_group.add_argument('--proxy-pass', dest='proxy_pass', help='proxy password')
proxy_group.add_argument('--proxy-host', dest='proxy_host', help='host or IP \
        with :port')
proxy_group.add_argument('--proxy-scheme', dest='proxy_scheme', help='Can be \
        \'socks5\' or \'sock5h\' (See python requests documentation for more \
        information')
proxy_group.add_argument('--proxy-conn', dest='proxy_conn', help='\'http\' or \
        \'https\'')
# Get config options from config file and load in defaults
jc_kwargs = get_json_config()
proxy_group.set_defaults(**jc_kwargs)
clargs = clp.parse_args()

# If 'title' and 'url' then add the link to the db
if (clargs.title and clargs.url) or (clargs.url):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if (clargs.gid): gid = clargs.gid
    else: gid = None
    try:
        with db(dbc, db_feed_table) as db_add:
            db_add.add_feed(gid, clargs.title, clargs.url, ts)
    except MySQLdb._exceptions.OperationalError:
        print("No mysql server connection found. Exiting.")
        sys.exit()
    sys.exit()

# if user is adding a group to 'groups' table in mysql
if (clargs.add_group):
    try:
        with db(dbc, db_group_table) as db_add:
            db_add.add_group(clargs.add_group)
    except MySQLdb._exceptions.OperationalError:
        print("No mysql server connection found. Exiting.")
        sys.exit()
    sys.exit()

if (clargs.delete_feed):
    try:
        with db(dbc, db_feed_table) as db_remove:
            db_remove.remove_feed(clargs.delete_feed)
    except MySQLdb._exceptions.OperationalError:
        print("Error with feed id removal. Exiting")
        sys.exit()
    sys.exit()

if clargs.list_groups:
    try:
        with db(dbc, db_group_table) as db_list:
            db_grouplist = db_list.get_all_groups()
        for (db_group_id, db_group_name) in db_grouplist:
            print("GID: " + str(db_group_id) + " " + db_group_name)
    except MySQLdb._exceptions.OperationalError:
        print(e)
    sys.exit(0)

# If output cmdline option is a filename
if clargs.output:
    try:
        sys.stdout = open(clargs.output, "w")
    except FileNotFoundError:
        print("No such file or directory'" + clargs.output + "'. Exiting")
        exit()

# Create the html header for font size etc if --html used
if clargs.html:
    print("<!DOCTYPE html><html><head>\
           <link rel=\"shortcut icon\" type=\"image/png\" \
            href=\"favicon.png\">\
            <style>\
            body { -webkit-text-size-adjust: 300%; }\
            p { font-family: Arial, Helvetica, sans-serif; fone-size: small; }\
            a { text-decoration: none; }\
            a:hover { text-decoration: underline; }\
        </style></head>")
    print("<?php\n" +
          "if ($_GET['delete'] == 1) {unlink(__FILE__);header('Location: " +
          str(clargs.website) + "');}\n" +
          "echo \"<table width=100%><tr><td align=right>" +
          "<a href='?delete=1'>delete?</a></td></tr></table>\"; ?>")

# Connect to database and get all feeds
try:
    with db(dbc, db_feed_table) as db:
        if clargs.feed_id:
            db_feedlist = db.get_all_feeds(feed_id=clargs.feed_id)
        elif clargs.group:
            db_feedlist = db.get_all_feeds(group=1)
            #show_groups = 1
        # Assuming '-a' here for all items even if not specified
        else:
            db_feedlist = db.get_all_feeds()
        # print (db_feedlist)
        # If listing all feeds from db then don't need a session
        if not clargs.list:
            session = requests.Session()
            session.proxies.update(get_proxy_info(**jc_kwargs))
 
        # with each feed from db_feedlist list feeds or print the rss items
        for (db_feed_id, db_feed_group_id, db_feed_title, db_feed_url,
                db_feed_comments, db_feed_dt) in db_feedlist:
            output_str = ""
            list_str = ""
            has_new_items = False
            if clargs.list:
                clargs.no_update = True
                if clargs.group:
                    list_str = "GID: " + str(db_feed_group_id) + ", "
                if clargs.verbose:
                    list_str += "ID: " + str(db_feed_id) + " " + \
                            db_feed_title + \
                            " (" + str(db_feed_dt) + ") " + \
                            db_feed_url
                else:
                    list_str += "ID: " + str(db_feed_id) + " " + \
                            db_feed_title + " (" + str(db_feed_dt) + ")"
                print(list_str)
            else:
                if clargs.html:
                    output_str += db_feed_title + "<br>"
                    if clargs.verbose:
                        print(db_feed_title + "<br>")
                else:
                    output_str += db_feed_title + "\n"
                    if clargs.verbose:
                        print(db_feed_title)
                item_dts.clear()
                try:
                    # response = requests.get(db_feed_url, timeout=5.0)
                    response = session.get(db_feed_url, timeout=15.0)
                    f = feedparser.parse(response.text)  # db_feed_url)
                except (URLError,
                        requests.exceptions.MissingSchema,
                        requests.exceptions.ConnectionError,
                        requests.exceptions.SSLError) as e:
                    if clargs.html:
                        excep_str = "Exception: (id: " + \
                                str(db_feed_id) + " - " + \
                                db_feed_url + "): " + \
                                str(e) + '<br>'
                    else:
                        excep_str = "Exception: (id: " + \
                                str(db_feed_id) + " - " + \
                                db_feed_url + "): " + \
                                str(e) + '\n'
                    #print("Exception: (" + db_feed_url + "): " + str(e) + '\n')
                    print(excep_str)
                    continue
                except requests.exceptions.Timeout as e:
                    print("Timeout from {0}. {1}\n".format(db_feed_url, e))
                    continue
                # With each rss item, convert the published date to a timestamp
                # and see if any links are newer than the db_feed_dt timestamp
                for item in f.entries:
                    # See issue# 151 https://github.com/kurtmckee/feedparser/issues/151
                    if item.updated_parsed == "":
                        print("item.updated_parsed is empty. db_feed_id: " + db_feed_id)
                    try:
                        item_dt = datetime.datetime.fromtimestamp(mktime(item.updated_parsed))
                    except (TypeError,
                            KeyError,
                            AttributeError,
                            OverflowError,
                            ValueError) as e:
                        print("Exception: " + str(e) + "\n" + "db_feed_id: " + str(db_feed_id))
                        print("item.updated_parsed: " + \
                                str(item.updated_parsed) + "\n")
                        item_dt = datetime.datetime.fromtimestamp(time.time())
                    # If the rss item timestamp is greater than the feed timestamp in db
                    # Add that item timestamp to the item_dts list to sort later
                    if item_dt > db_feed_dt:
                        has_new_items = True
                        # TODO: do try/except over the item.link as sometimes it
                        #       is not always present (KeyError)
                        if clargs.html:
                            if clargs.comments:
                                try:
                                    output_str += link_html((item.link, item.title, item_dt), item.comments)
                                except AttributeError:
                                    output_str += link_html((item.link, item.title, item_dt))
                            else:
                                output_str += link_html((item.link, item.title, item_dt))
                        else:
                            if clargs.comments:
                                try:
                                    output_str += "  -" + item.title + "\n   " + \
                                          item.link + " (" + str(item_dt) + \
                                          "),\n   Comments: " + item.comments + "\n"
                                except AttributeError:
                                    output_str += "  -" + item.title + "\n   " + \
                                          item.link + " (" + str(item_dt) + ")\n"
                            else:
                                output_str += "  -" + item.title + "\n   " + \
                                      item.link + " (" + str(item_dt) + ")\n"
                        # list of datetime stamps to update the feed.updated field
                        item_dts.append(item_dt)
                        item_list = [item.title, item.link, item_dt]
                # item_dts may be empty if no new rss items
                try:
                    max_dt = max(item_dts)
                    if not clargs.no_update:
                        db.update_feed_dt(db_feed_id, max_dt)
                except ValueError:
                    if clargs.html:
                        output_str += "No new items<br>"
                    else:
                        output_str += "No new items\n"
                if clargs.html:
                    output_str += "<hr>"
                else:
                    output_str += "-------------------------------------------"
                # Output the feeds depending if user wants all feeds or not
                if not clargs.all_feeds and has_new_items:
                    print(output_str)
                elif not clargs.all_feeds and not has_new_items:
                    pass
                elif clargs.all_feeds:
                    print(output_str)
        if not clargs.list: session.close()
except OperationalError:
    print("No mysql server connection found. Exiting.")
    exit()
