# rss-checker
Python script that uses mysql/maria db to show only new rss feeds from last update

The script does the following:
- Keeps a mysql/maria db of the feeds that you want to track.
- Keeps a list of those topics/urls/articles that are in each feed and will show the differences (new links that were added) compared to the last time you ran the script.

You can add rss feeds to the script/db so you can track that feed for new rss links. 
This would be good for a cronjob that you can run to email you the new articles in the rss feed.
