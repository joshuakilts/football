import json
import pandas as pd


with open('data/fantasypros/players/players.json', 'r') as f:
    players_json = json.load(f)
    
players = pd.DataFrame(players_json['players'])


reddit_comments = pd.read_json('data/reddit/reddit_comments.json')
reddit_submissions = pd.read_json('data/reddit/reddit_submissions.json')
tweets = pd.read_csv('data/twitter/tweets.csv')


# projections and consensus
positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DST']

projections_dfs = []
consensus_dfs = []
for position in positions:
    with open('data/fantasypros/projections/{}.json'.format(position), 'r') as f:
        projections_json = json.load(f)
    
    projections_df = pd.DataFrame(projections_json['players'])
    projections_dfs.append(projections_df)
    
    with open('data/fantasypros/consensus/{}.json'.format(position), 'r') as f:
        consensus_json = json.load(f)
    
    consensus_df = pd.DataFrame(consensus_json['players'])
    consensus_dfs.append(consensus_df)


projections = pd.concat(projections_dfs)
consensus = pd.concat(consensus_dfs)


# transform reddit data
reddit_submissions = reddit_submissions.explode('players').drop_duplicates()
reddit_submissions['body'] = reddit_submissions.selftext + ' ' + reddit_submissions.title
reddit_submissions = reddit_submissions[['body', 'players', 'created']].groupby('players').agg({'body': lambda x: ' '.join(x), 'created': 'count'})
reddit_submissions = reddit_submissions.rename(columns = {'created': 'submission_count', 'body': 'submission_text'})

reddit_comments = reddit_comments.explode('players').drop_duplicates()
reddit_comments = reddit_comments[['body', 'players', 'created']].groupby('players').agg({'body': lambda x: ' '.join(x), 'created': 'count'})
reddit_comments = reddit_comments.rename(columns = {'created': 'comment_count', 'body': 'comments_text'})



# transform twitter data
tweets = tweets.drop_duplicates()
tweets = tweets[['created', 'body', 'p_id']].groupby('p_id').agg({'body': lambda x: ' '.join(x), 'created': 'count'})
tweets = tweets.rename(columns = {'created': 'tweet_count', 'body': 'tweets_text'})


# explode json column "stats" into separate columns
projections = pd.concat([projections, projections.stats.apply(pd.Series)], axis = 1)
projections = pd.concat([projections, projections.stats.apply(pd.Series)], axis = 1)
projections = projections.drop(columns = ['mflid', 'name', 'position_id', 'team_id', 'filename', 'stats',
                                          'position_id', 'team_id', 'filename'])


consensus = consensus.drop(columns = ['player_name','sportsdata_id','player_team_id','player_position_id',
                                      'player_positions','player_short_name','player_eligibility','player_yahoo_positions',
                                      'player_page_url','player_filename','player_square_image_url','player_image_url',
                                      'player_yahoo_id','cbs_player_id','player_bye_week','rank_ecr'])


players = players.set_index('player_id').join(consensus.set_index('player_id'))
players = players.join(projections.set_index('fpid'))
players = players.join(tweets)
players = players.reset_index()
players = players.set_index('player_name').join(reddit_submissions)
players = players.join(reddit_comments).reset_index()