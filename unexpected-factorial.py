import logging
import re
import math
import praw
from praw.models import MoreComments
from decimal import Decimal

import config


REGEX = r"(\d+!)"
MAX_FACTORIAL = 100000


def main():
	'''handler = logging.StreamHandler()
	handler.setLevel(logging.DEBUG)
	logger = logging.getLogger('prawcore')
	logger.setLevel(logging.DEBUG)
	logger.addHandler(handler)'''

	reddit = praw.Reddit(user_agent = config.reddit['user_agent'],
                     	client_id = config.reddit['client_id'], client_secret = config.reddit['client_secret'],
                    	 username = config.reddit['username'], password = config.reddit['password'])
                         
	subreddit = reddit.subreddit(config.reddit['subreddit'])
	for comment in subreddit.stream.comments():
		if isinstance(comment, MoreComments):
			continue
		if check_condition(comment) and check_unresponded(comment):
			bot_action(comment)

##return true if there is at least one matching instance of the regex contained in the string
def check_condition(comment):
	if comment.author == config.reddit['username']:
		return False
	if re.search(REGEX, comment.body) is None:
		return False
	return True

#return true if we have not responded to this thread
def check_unresponded(comment):
	comment.refresh()
	for top_level_reply in comment.replies:
		if isinstance(top_level_reply, MoreComments):
			continue
		if top_level_reply.author.name == config.reddit['username']:
			return False
	return True


def bot_action(comment):
	matchedExpressions = re.findall(REGEX, comment.body)
	replyBody = "Warning! Factorials in the comments may be larger than they appear...\n"
	for expression in matchedExpressions:
		f = float(expression.rstrip('!'))
		if f > MAX_FACTORIAL:
			f = "[Wolfram Result](http://www.wolframalpha.com/input/?i=" + expression + ")"
		elif f < 15:
			f = format(math.factorial(f))
		else:
			f = "{:.2E}".format(Decimal(math.factorial(f)))
			
		replyBody += ">" + expression + "\n\n" + expression + " = " + f + "\n"

	comment.reply(replyBody)
	return

if __name__ == '__main__':
    main()