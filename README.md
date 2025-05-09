# rss-checker
Python script that uses feedparser and mysql/maria db to show only new rss feeds from last update

The script does the following:
- Keeps a mysql/maria db of the feeds that you want to track.
- The mysql feed.updated field keeps the latest rss item 'published' date that the script last checked. So unless there are new items added to the feed, it will not show you any new items. The script doesn't keep an rss list of items as there is no need to because of comparing the feed.updated datetime field against the rss item 'published' date.

You can add rss feeds to the script/db so you can track that feed for new rss links.
This would be good for a cronjob that you can run to email you the new articles in the rss feed.

You can group your feeds together in groups so the feeds show in groups instead of how they were added.

### Command line options:
```
Adding a feed:
  [-t | --title] TITLE: Add a feed title
  [-u | --url] LINK: Add a feed url/link
  [--gid] When adding a feed using -u or -t above, put the feed in group 'gid'.
  Use --list-groups to see list of groups
  [--add-group GROUP_NAME] Name of group to add
  NOTE: You can add a feed with just a --url and no --title

Running script:
  no options: Checks all rss feeds in db and sees if there are any new links added
  [-a | --all-feeds]: Show all feeds in output even if they don't have any new rss items.
  [-c | --comments]: Provide link to rss item comments if available
  [-f | --feed-id] FEED_ID: Only use or check this feed id
  [-g | --group]: Group feeds together
  [--html]: output html links within script output for clickable links for sending in an email
  [-l | --list]: List all feeds
  [--list-groups]: List all group names and group_id
  [-n | --no-update]: Don't update the feed with a time stamp
  [-o | --output] TMP_FILE: temporary file location to write to disk instead of stdout
  [-v | --verbose]: Be a little more verbose
```
### Database setup:
Run as root under mysql:
```
CREATE USER rss_checker@localhost IDENTIFIED BY 'password';
GRANT ALL ON rss_checker.* TO rss_checker@localhost;
```
Logout as root from mysql and then run:
```$ mysql -u rss_checker -p < db.sql```

### Initial Usage (to add a feed to the db):
<code>$ rss-checker.py -t 'Feed title' -u 'https://link.to.my.feed.url'</code>

### Usage:
<code>$ rss-checker.py</code> to check for any new rss items that are in the feed compared to the last update from the feed url. The default is to write to stdout.

<code>$ rss-checker.py --add-group "Technology News Feeds"</code> Add a rss group

<code>$ rss-checker.py --list-groups</code> List all rss groups in db

<code>$ rss-checker.py -u 'https://link.to.my.feed.url' -t 'Hot News Feed' --gid 1</code> Add a rss feed and add to group gid=1

<code>$ rss-checker.py --list</code> List all feeds with id

<code>$ rss-checker.py --list -f3</code> List only feed with feed_id = 3

### Cron usage (example):
<code>$ rss-checker.py -o /tmp/rss.txt; sed -i 's/$/<br>/' && mutt -e 'set content_type=text/html' -s "test rss-checker output " EMAIL_ADD < /tmp/rss.txt</code>
