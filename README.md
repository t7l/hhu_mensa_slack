# hhu_mensa_slack
Scrape canteen menu of Heinrich Heine University Duesseldorf daily and push it to Slack

hhu_mensa_slack is a small tool to fetch information about today's menu from the webpage of the canteen (Mensa) of the Heinrich Heine University Duesseldorf and push it to a Slack channel.

The easiest way to install this is by creating a Heroku app:


First, the following environment variables are required:

- `SLACK_CHANNEL`: The name of the channel to post into.

- `SLACK_TOKEN`: The Slack token (https://api.slack.com/custom-integrations/legacy-tokens).

- `NOTIFY_SCHEDULE`: The time the bot should post into the channel (Germany time e.g. "17:30").


Second, you need this buildpack: https://github.com/heroku/heroku-buildpack-locale.

Finally, just clone this repository and make sure the worker dyno is running. Thats it.