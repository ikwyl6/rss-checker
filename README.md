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
  -t: feed title
  -l: feed url/link

Running script:
  no options: Checks all rss feeds in db and sees if there are any new links added
  -f: temporary file location to write to disk instead of stdout
  -h: output html links within script output for clickable links for sending in an email
```

### Initial Usage:
<code>rss-checker.py -t 'Feed title' -l 'https://link.to.my.feed.url'</code>

### Usage:
<code>$ rss-checker.py</code> to check for any new rss items that are in the feed compared to the last update from the feed url. The default is to write to stdout.

### Cron usage (example):
<code>$ rss-checker.py -f /tmp/rss.txt; sed -i 's/$/<br>/' && mutt -e 'set content_type=text/html' -s "test rss-checker output " EMAIL_ADD < /tmp/rss.txt
