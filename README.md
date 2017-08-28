# hhu_mensa_slack
Scrape canteen menu of Heinrich Heine University Duesseldorf daily and push it to Slack

hhu_mensa_slack is a small tool to fetch information about today's menu from the webpage of the canteen (Mensa) of the Heinrich Heine University Duesseldorf and push it to a Slack channel.

The tool has been tested only on (Debian) Linux. You need to install the german locale de_DE.utf8 to use it.

To get a message every day when you may get hungry, use a cronjob to push the menu to Slack, e.g. like this (you may have to change the path to your python interpreter and the location of the script):
```
00 11 * * 1-5 python /opt/hhu_mensa_slack.py
```
11 o'clock is imho a good time as the canteen opens at 11:30. :)