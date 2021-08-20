import tweepy
import json
import sys
sys.path.append("..")
import pandas as pd
from time import sleep
from creds.twitter_creds import twitter_creds

consumer_key, consumer_secret, access_token, access_token_secret = twitter_creds

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


# get player names
with open('../data/fantasypros/players/players.json', 'r') as f:
    players = json.loads(f.read())



search_terms = []
for player in players['players']:
    if player['position_id'] == 'DST':
        search_terms.append([player['player_id'], player['player_name'] + ' dst'])
        search_terms.append([player['player_id'], player['player_name'] + ' defense'])
    else:
        search_terms.append([player['player_id'], player['player_name']])


parsed_records = []
completed_searches = []
counter = 0
for p_id, p_name in search_terms:
    for page in tweepy.Cursor(api.search, q = p_name, count = 100, result_type = 'recent', tweet_mode = 'extended').pages():
        for result in page:
            result = result._json
            parsed_record = [result['created_at'], result['id_str'], result['full_text'], result['retweet_count'], result['favorite_count'], p_id]
            parsed_records.append(parsed_record)

            sleep(1)

    completed_searches.append([p_id, p_name])
    
    counter += 1
    if counter % 10 == 0:
        print('{}/{}'.format(counter, len(search_terms)))
    
    
    
pd.DataFrame(parsed_records, columns = ['created', 'id_str', 'body', 'retweets', 'favorites', 'p_id']).to_csv('../data/twitter/tweets.csv', index = False)