import os
import time
import re
import logging
import flickrapi
import flickrapi.shorturl
import random
from slackclient import SlackClient

api_key = os.environ.get('FLICKR_KEY')
api_secret = os.environ.get('FLICKR_SECRET') 

logging.basicConfig()

animals = []

for line in open(os.environ.get('ANIMALS_FILE')):
	animals.append(line.rstrip())

animals_re = '(' + "|".join(animals) + ')';

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
	"""
		Parses a list of events coming from the Slack RTM API to find bot commands.
		If a bot command is found, this function returns a tuple of command and channel.
		If its not found, then this function returns None, None.
	"""
	for event in slack_events:
		if event["type"] == "message" and not "subtype" in event:
			user_id, message = parse_direct_mention(event["text"])
			if user_id == starterbot_id:
				return message, event["channel"]
	return None, None

def parse_direct_mention(message_text):
	"""
		Finds a direct mention (a mention that is at the beginning) in message text
		and returns the user ID which was mentioned. If there is no direct mention, returns None
	"""
	matches = re.search(MENTION_REGEX, message_text)
	# the first group contains the username, the second group contains the remaining message
	return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
	"""
		Executes bot command if the command is known
	"""

	random_animal = random.choice(animals)

	# Default response is help text for the user
	response = "I'm sorry. I didn't understand. Try *{}* or 'suprise me'." . format(random_animal)
	attachments = None

	animal = None
	extra = ""

	if re.search('(please|thank|welcome)', command, re.IGNORECASE):
		slack_client.api_call(
			"chat.postMessage",
			channel=channel,
			text="AnimalBot enjoys finding animals for you"
			)

	if re.search('penguin', command, re.IGNORECASE):
		slack_client.api_call(
			"chat.postMessage",
			channel=channel,
			text=":penguin: coming up"
			)


	if re.search('surprise me', command, re.IGNORECASE):
		animal = random_animal
   
	if not animal: 
		a = re.search(animals_re, command, re.IGNORECASE)
		if a:
			animal = a.group(1) 
	
	a = re.search("with ([^.]+)(\.|$)", command, re.IGNORECASE)
	if a:
		extra = a.group(1)

	# This is where you start to implement more commands!
	if animal:
		response = None
		url_c = None
		url = ''

		ran = random.randint(1,201)
		i = 0

		tags = animal
		if extra:
			tags = tags + ',' + extra

		flickr = flickrapi.FlickrAPI(api_key, api_secret)
		for photo in flickr.walk(text='animal',
				per_page=200,
				tags=tags,
				tag_mode='all',
				license='1,2,3,4', # https://www.flickr.com/services/api/flickr.photos.licenses.getInfo.html
				extras='url_c',
				sort='relevance'):

			i = i+1

			if i >= ran and photo.get('url_c'):
				url_c = photo.get('url_c')
				url = flickrapi.shorturl.url(photo.get('id'))

				break
        
		if url: 
			title = animal
			if extra:
				title = title + ' with ' + extra

			attachments = [{"title": title + " for you ("+ url + ")", "image_url": url_c }]
		else:
			response = "I am deeply sorry but I could not find an animal for you. Please try again."

	# Sends the response back to the channel
	slack_client.api_call(
			"chat.postMessage",
			channel=channel,
			attachments=attachments,
			text=response
			)

if __name__ == "__main__":
	if slack_client.rtm_connect(with_team_state=False):
		print("Starter Bot connected and running!")
		# Read bot's user ID by calling Web API method `auth.test`
		starterbot_id = slack_client.api_call("auth.test")["user_id"]
		while True:
			command, channel = parse_bot_commands(slack_client.rtm_read())
			if command:
				handle_command(command, channel)
			time.sleep(RTM_READ_DELAY)
	else:
		print("Connection failed. Exception traceback printed above.")
