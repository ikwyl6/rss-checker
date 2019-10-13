# rss-notifier
Python script that uses mysql/maria db to show only new rss feeds from last update

The script does the following:
- Keeps a mysql/maria db of the feeds that you want to track.
- Keeps a list of those topics/urls that are in each feed and will show the differences (new links that were added) compared to the last time you ran the script.

