# AnimalBot

AnimalBot is a Slack Bot that finds Flickr images that match direct messages sent to it.

Installation:

1. spin up new EC2 linux instance
2. sudo yum install git
3. sudo yum install python-pip
4. sudo yum install python-virtualenv
5. mkdir animalbot
6. checkout this repo
7. virtualenv animalbot
8. source animalbot/bin/activate
9. pip install slackclient
10. pip install flickrapi
11. export SLACK_BOT_TOKEN=''
12. export FLICKR_KEY=''
13. export FLICKR_SECRET=''

Inspired by https://www.fullstackpython.com/blog/build-first-slack-bot-python.html

Using https://github.com/hzlzh/Domain-Name-List/blob/master/Animal-words.txt for list of animals


