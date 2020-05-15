# rss-checker
Python script that uses feedparser and mysql/maria db to show only new rss feeds from last update

The script does the following:
- Keeps a mysql/maria db of the feeds that you want to track.
- The mysql feed.updated field keeps the latest rss item 'published' date that the script last checked. So unless there are new items added to the feed, it will not show you any new items. The script doesn't keep an rss list of items as there is no need to because of comparing the feed.updated datetime field against the rss item 'published' date. 

You can add rss feeds to the script/db so you can track that feed for new rss links. 
This would be good for a cronjob that you can run to email you the new articles in the rss feed.

### Command line options:
```
Adding a feed:
  [-t | --title] TITLE: Add a feed title
  [-u | --url] LINK: Add a feed url/link
  NOTE: You can add a feed with just a --url and no --title

Running script:
  no options: Checks all rss feeds in db and sees if there are any new links added
  [-o | --output] TMP_FILE: temporary file location to write to disk instead of stdout
  [-n | --no-update]: Don't update the feed with a time stamp
  [-a | --all-feeds]: Show all feeds in output even if they don't have any new rss items.
  [-f | --feed-id] FEED_ID: Only use or check this feed id
  [-l | --list]: List all feeds
  [-c | --comments]: Provide link to rss item comments if available
  --html: output html links within script output for clickable links for sending in an email
```
### Database setup:
Run as root under mysql: 
```
CREATE USER rss_checker@localhost IDENTIFIED BY 'password';
GRANT ALL ON rss_checker.* TO rss_checker@localhost;
```
Logout as root from mysql and then run:
```$ mysql -u rss_checker -p < rss-checker.sql```

### Initial Usage:
<code>$ rss-checker.py -t 'Feed title' -u 'https://link.to.my.feed.url'</code>

### Usage:
<code>$ rss-checker.py</code> to check for any new rss items that are in the feed compared to the last update from the feed url. The default is to write to stdout.

<code>$ rss-checker.py --list</code> List all feeds with id

<code>$ rss-checker.py --list -f3</code> List only feed with feed_id = 3

### Cron usage (example):
<code>$ rss-checker.py -o /tmp/rss.txt; sed -i 's/$/<br>/' && mutt -e 'set content_type=text/html' -s "test rss-checker output " EMAIL_ADD < /tmp/rss.txt
