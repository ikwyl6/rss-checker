# rss-checker
Python script that uses mysql/maria db to show only new rss feeds from last update

The script does the following:
- Keeps a mysql/maria db of the feeds that you want to track.
- The mysql feed.updated field keeps the latest rss item 'published' date that the script last checked. So unless there are new items added to the feed, it will not show you any new items. The script doesn't keep an rss list of items as there is no need to because of comparing the feed.updated datetime field against the rss item 'published' date. 

You can add rss feeds to the script/db so you can track that feed for new rss links. 
This would be good for a cronjob that you can run to email you the new articles in the rss feed.
