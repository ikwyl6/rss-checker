#!/bin/python

import MySQLdb as mysql
from MySQLdb import OperationalError


class db:

    feed_table = ""

    def __init__(self, dbc, feed):
        self.con = mysql.connect(host=dbc[0], user=dbc[1], passwd=dbc[2], db=dbc[3])
        self.feed_table = feed
        #self.rss_table = rss
        self.cursor = self.con.cursor()

    # called when you enter a 'with' command
    def __enter__(self):
        return self

    # called when you finish with a 'with' command
    def __exit__(self,type,value,trackback):
        self.cursor.connection.close()

    # get all groups
    def get_all_groups(self):
        self.cursor.execute("SELECT * FROM groups;", )
        return self.cursor.fetchall()

    # get all rss feeds from db
    def get_all_feeds(self, **kwargs):
        feed_id = kwargs.get('feed_id', None)
        group = kwargs.get('group', None)
        if (feed_id): 
            sql = "SELECT * FROM " + self.feed_table + " WHERE id = '" + feed_id + "';"
        elif (group):
            sql = "SELECT * FROM " + self.feed_table + " ORDER BY group_id ASC;"
        else: sql = "SELECT * FROM " + self.feed_table + ";"
        self.cursor.execute(sql, )
        return self.cursor.fetchall()

    def get_feed(self, feed_id):
        self.cursor.execute("SELECT * FROM " + self.feed_table + " WHERE id = " + feed_id + ";")
        return self.cursor.fetchall()

    # Add feed/link to feed_table
    def add_feed(self, gid, feed_title, feed_url, feed_ts):
        if (feed_title is None): feed_title = ""
        feed_title = feed_title.replace("'", "''")
        sql ="INSERT INTO " + self.feed_table + \
            " (title,url,updated) VALUES ('" + feed_title + "', '" + \
            feed_url + "', '" + feed_ts + "')" 
        if (gid):
            sql ="INSERT INTO " + self.feed_table + \
                " (group_id,title,url,updated) VALUES ('" + str(gid) + "', '" + \
                feed_title + "', '" + feed_url + "', '" + feed_ts + "')" 
        self.cursor.execute(sql, )
        self.con.commit()
   
    # Add group
    def add_group(self, group_name):
        group_name = group_name.replace("'", "''")
        sql = "INSERT INTO groups (name) VALUES ('" + group_name + "')"
        self.cursor.execute(sql, )
        self.con.commit()

#    def add_item(self,feed_id, item):
#        sql = "INSERT INTO " + self.rss_table + " (feed_id, title, url, published) VALUES ('" \
#                + str(feed_id) + "', '" + item[0] + "', '" + item[1] + "', '" + str(item[2]) + "');"
#        self.cursor.execute(sql, )
#        self.con.commit()

    # Update feed timestamp
    def update_feed_dt(self,feed_id, dt):
        sql = "UPDATE " + self.feed_table + " SET updated = '" + str(dt) + "' WHERE id = '" + str(feed_id) + "';"
        self.cursor.execute(sql, )
        self.con.commit()
