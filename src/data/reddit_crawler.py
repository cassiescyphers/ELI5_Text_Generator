import praw
import os 
import yaml


class RedditCrawler:
    def __init__(self, keys_file, subreddit_name):
        self.keys_file = keys_file
        self.keys = self.load_keys()
        self.subreddit_name = subreddit_name
        self.subreddit = self.initialize_subreddit_scraper()
        
    def load_keys(self):
        try:
            keys = self.load_yaml()
        except FileNotFoundError:
            raise('Key file not found.')
        return keys

    def load_yaml(self):
        with open(self.keys_file, 'r') as f:
            result = yaml.safe_load(f)
        return result


    def initialize_subreddit_scraper(self):
        client_secret = self.keys['secret key']
        client_id = self.keys['personal use script']
        user_agent = self.keys['name']
        username = self.keys['username']
        password = self.keys['password']

        self.reddit = praw.Reddit(client_id=client_id,
                             client_secret=client_secret,
                             user_agent=user_agent,
                             username=username,
                             password=password)

        subreddit = self.reddit.subreddit(self.subreddit_name)

        return subreddit

