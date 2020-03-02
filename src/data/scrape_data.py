import praw
import sys
import pandas as pd
import os 
import yaml
from tqdm import tqdm
import pickle
from reddit_crawler import RedditCrawler

SEARCH_TERMS = ['machine learning',
                'deep learning', 
                'neural network', 
                'neural networks', 
                'dnn','rnn','lstm', 
                'artificial intelligence', 
                'a.i.', 
                'ai']


def find_relevant_threads(subreddit):
    all_submissions = []
    for sub_query in SEARCH_TERMS:
        search_results = subreddit.search(sub_query, 
                                          sort='new', 
                                          time_filter='all', 
                                          limit=None)
        for submission in search_results:
            all_submissions = all_submissions + [submission]

    return set(all_submissions)
    
def load_submission_ids_into_df(submissions):
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
    

def dump_pickle(data, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

def load_text_from_submissions(submission_df, reddit):
    all_questions = []
    all_comments = []
    for i in tqdm(range(len(submission_df))):
        submission_id = submission_df.iloc[i].name
        submission = praw.models.Submission(reddit, id = submission_id)
        comments = [comment.body for comment in submission.comments if (hasattr(comment, "body") and comment.distinguished==None)]
        all_questions.append(submission.title)
        all_comments.append(comments)
        
    return all_questions, all_comments

def main(output_dir, keys_file):
    crawler = RedditCrawler(keys_file, 'explainlikeimfive')
    
    print('Finding relevant threads')
    eli5_ml_threads = find_relevant_threads(crawler.subreddit)
            
    print('saving submission lookup table to {}'.format(output_dir))
    submission_df = load_submission_ids_into_df(eli5_ml_threads)
    submission_df.to_csv(os.path.join(output_dir, 'submission_df_lookup.csv'))
    
    print('getting text from the threads')
    all_questions, all_comments = load_text_from_submissions(submission_df, crawler.reddit)
    
    print('saving text to {}'.format(output_dir))
    dump_pickle(all_questions, os.path.join(output_dir, 'all_questions.pickle'))
    dump_pickle(all_comments, os.path.join(output_dir, 'all_comments.pickle'))
    
                         
if __name__ == '__main__':
    output_dir = sys.argv[1]
    keys_file = sys.argv[2]
    main(output_dir, keys_file)
    
    
    