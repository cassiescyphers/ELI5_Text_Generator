import praw
import sys
import pandas as pd
import os 
import yaml


SEARCH_TERMS = ['machine learning',
                'deep learning', 
                'neural network', 
                'neural networks', 
                'dnn','rnn','lstm', 
                'artificial intelligence', 
                'a.i.', 
                'ai']



class RedditCrawler:
    def __init__(self):
        self.search_terms = SEARCH_TERMS
        self.keys_file = '../../keys/reddit_keys.yml'
        self.keys = self._load_keys()
        self.subreddit = self._initialize_subreddit_scraper()
        
    def _load_keys(self):
        keys = self._load_yaml()

        return keys

    def _load_yaml(self):
        with open(self.keys_file, 'r') as f:
            result = yaml.safe_load(f)
        return result


    def _initialize_subreddit_scraper(self):
        client_secret = self.keys['secret key']
        client_id = self.keys['personal use script']
        user_agent = self.keys['name']
        username = self.keys['username']
        password = self.keys['password']

        reddit = praw.Reddit(client_id=client_id,
                             client_secret=client_secret,
                             user_agent=user_agent,
                             username=username,
                             password=password)

        subreddit = reddit.subreddit('explainlikeimfive')

        return subreddit

    def find_relevant_threads(self):
        all_submissions = []
        for sub_query in self.search_terms:
            search_results = self.subreddit.search(sub_query, 
                                                  sort='new', 
                                                  time_filter='all', 
                                                  limit=None)
            for submission in search_results:
                all_submissions = all_submissions + [submission]

        return set(all_submissions)
    
    def load_submission_ids_into_df(self, submissions):
        ids = [thread.id for thread in submissions]
        num_comments = [thread.num_comments for thread in submissions]
        num_upvotes = [thread.ups for thread in submissions]
        num_downvotes = [thread.downs for thread in submissions]
        df = pd.DataFrame(data={'id':ids, 
                                'num_comments': num_comments, 
                                'num_upvotes': num_upvotes,
                                'num_downvotes':num_downvotes})
        df = df.set_index('id')
        df = df.sort_values(by='num_comments', ascending=False)

        return df

def main(output_dir):
    crawler = RedditCrawler()
    
    print('Finding relevant threads')
    eli5_ml_threads = crawler.find_relevant_threads()
    
    print('saving data to {}'.format(output_dir))
    submission_df = crawler.load_submission_ids_into_df(eli5_ml_threads)
    submission_df.to_csv(os.path.join(output_dir, 'submission_df_lookup.csv'))
                         
if __name__ == '__main__':
    output_dir = sys.argv[1]
    main(output_dir)
    
    
    