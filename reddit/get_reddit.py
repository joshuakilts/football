import psaw
import json
import re
from datetime import datetime


# get player names & create list of terms to search for
with open('../data/fantasypros/players/players.json', 'r') as f:
    players = json.loads(f.read())
    
players_list = []
for player in players['players']:
    if player['position_id'] == 'DST':
        players_list.append([player['player_id'], player['player_name'] + ' dst'])
        players_list.append([player['player_id'], player['player_name'] + ' defense'])
    else:
        players_list.append([player['player_id'], player['player_name']])


# breaks a list into chunks of size n
def partition_list(list_in, n):
    list_out = []
    for i in range(0, len(list_in), n):
        list_out.append(list_in[i:i+n])
    
    return list_out


# break players list into chunks of 100 (reddit api only takes 100 at a time)
players_lists = partition_list(players_list, 100)
search_queries = []
for chunk in players_lists:
    
    chunk = [x[1] for x in chunk]
    search_query = '|'.join(chunk)
    search_queries.append(search_query)


# set list of subreddits to search
subreddits = ['fantasyfootball', 'nfl']
subreddit_query = ','.join(subreddits)

# set date to search after
after = int(datetime(2021, 8, 4).timestamp())


# walk through search queries and find all submissions/comments
submissions = []
comments = []
counter = 0
for search_query in search_queries:
    
    if counter % 5 == 0:
        print('{}/{}'.format(counter, len(search_queries)))
    counter += 1
    
    api = psaw.PushshiftAPI()
    sub_gen = api.search_submissions(
        q = search_query,
        subreddit = subreddit_query,
        after = after,
        filter=['author', 'selftext', 'title', 'created_utc', 'score', 'subreddit', 'id']
    )    
    
    caches = []
    for cache in sub_gen:
        caches.append(cache)
    
    if len(caches) > 0:

        for cache in caches:
            dict_idx = len(cache) - 1
            temp_dict = cache[dict_idx]

            if isinstance(temp_dict, dict):

                submissions.append(temp_dict)
                
            else:
                print('Not dict, type is {}'.format(type(temp_dict)))
                
    else:
        pass


    com_gen = api.search_comments(
        q = search_query,
        subreddit = subreddit_query,
        after = after,
        filter=['author', 'body', 'title', 'created_utc', 'score', 'subreddit', 'link_id']
    )

    caches = []
    for cache in com_gen:
        caches.append(cache)

    if len(caches) > 0:

        for cache in caches:
            dict_idx = len(cache) - 1
            temp_dict = cache[dict_idx]

            if isinstance(temp_dict, dict):
                
                comments.append(temp_dict)
            
            else:
                print('Not dict, type is {}'.format(type(temp_dict)))

    else:
        pass


player_names = [x[1] for x in players_list]


submissions_t = []
for submission in submissions:
    
    body = submission['selftext'] + ' ' + submission['title']
    
    players_found = [player for player in player_names if player.lower() in body.lower()]
        
    submission['players'] = players_found
    
    submissions_t.append(submission)


comments_t = []
for comment in comments:
    
    body = comment['body']
    
    players_found = [player for player in player_names if player.lower() in body.lower()]
        
    comment['players'] = players_found
    
    comments_t.append(comment)


with open('../data/reddit/reddit_submissions.json', 'w') as f:
    json.dump(submissions_t, f)

with open('../data/reddit/reddit_comments.json', 'w') as f:
    json.dump(comments_t, f)