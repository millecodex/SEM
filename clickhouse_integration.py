#!/usr/bin/env python
# coding: utf-8

# In[ ]:


'''
# W O R K   F L O W  #
1. download github data in native clickhouse format (74.6 gb, ~10hours to download)
2. clickhouse server must be running
see: https://clickhouse.tech/docs/en/getting-started/install/
 >sudo service clickhouse-server start (may need sudo -u japple)
 >clickhouse-client
# Insert the database into clickhouse
3. create the db tables:
 >CREATE TABLE github_events ...
see https://github-sql.github.io/explorer/#install-clickhouse
4. Insert the DB file into clickhouse <E:\Documents\Clickhouse Github data\github_events_v2.native.xz>
5. run code here to connect to clickhouse client and manipulate data
#
# Note the clickhouse driver (python) communicates with the clickhouse server via a native TCP/IP protocol 
# that ships data as typed values; this will cause problems when INSERT-ing into a DB, however I don't see
# this as an issue
'''


# In[83]:


from sqlalchemy import create_engine
from clickhouse_driver import Client
# dependencies
# >ipython-sql
# install by command prompt:
# >conda install -yc conda-forge ipython-sql
client = Client('localhost')


# In[ ]:


# load CSV file into dataframe
# get test dataframe with different repos
#  loop through dataframe
#   pull repo
#   build query
#   run query
#   write to dataframe


# In[ ]:


import pandas as pd
# not yet needed here
import time
import math


# In[ ]:


# Read CSV file into DataFrame df
# 200_repos_ready.csv has no index, CMC_id is in first column
# NaN is assigned to empty cells
dfs = pd.read_csv('200_repos.csv', index_col=0)


# In[ ]:


df = dfs[['repo','forge']].copy()


# In[ ]:


# subset dataframes for testing
# use .copy() as slicing will not allow for assignment
df10 = df.iloc[:10].copy()
df33 = df.iloc[:33].copy()


# In[ ]:


query_stars_L = '''
SELECT 
    count() 
FROM github_events 
WHERE event_type = 'WatchEvent' 
    AND repo_name ='''
query_stars_R = '''
GROUP BY action
'''
repo = '''
'HuobiGroup/huobi-eco-chain' 
'''


# In[203]:


query_test_noStars = '''
SELECT 
    count() 
FROM github_events 
WHERE event_type = 'WatchEvent' 
    AND repo_name =
'millecodex/SEM'
GROUP BY action
'''


# In[ ]:


query2 = '''
SELECT 
    count() 
FROM github_events 
WHERE event_type = 'WatchEvent' 
    AND repo_name =
'HuobiGroup/huobi-eco-chain'
GROUP BY action
'''


# In[206]:


res=client.execute(query_test_noStars)
if not res: print('not')


# In[ ]:


# test query that returns empty list (no results)
if not res2: print('not')


# In[ ]:


# Write a function for this
#
# initialize new column to null/None
df['stars']=None
# iterate the dataframe as follows:
'''
loop through dataframe
  pull repo
  build query
  run query
  update dataframe
'''
for row in df.itertuples():
    # only github for now as client is connected to github_events DB
    if row.forge == 'github':
        stars = 0
        repo = row.repo
        # skip the NaN repos
        if type(repo) == str:
            query = query_stars_L + '\''+repo+'\'' + query_stars_R
            stars = client.execute(query)
            # query returns a tuple of list elements accessible by [first list][first item]
            # no stars returns an empty list
            if not stars:
                df.at[row.Index, 'stars'] = 0
            else: df.at[row.Index, 'stars'] = stars[0][0]


# In[ ]:


# write update to 200_copy_stars.csv
# note beginning of script: pd.read_csv('200_repos_ready.csv', index_col=0)
df.to_csv('200_stars.csv', encoding='utf-8', index=1)
df


# In[ ]:


# Read in 200_repos.csv 
# has no index, CMC_id is in first column
dfr = pd.read_csv('200_repos.csv', index_col=0)
# new df with only 2 columns
# 'CMC_id' as index is maintained
df = dfr[['repo','forge']].copy()


# In[ ]:


query_forks_L = '''
SELECT 
    count() AS forks 
FROM github_events 
WHERE event_type = 'ForkEvent' AND repo_name =
'''
query_forks_R = '''
'curvefi/curve-dao-contracts/tree/master/doc'
'''
query_forks = query_forks_L + query_forks_R
query_forks


# In[ ]:


result=client.execute(query_forks)
print(result)


# In[ ]:


# Write a function for this
#
# initialize new column to null/None
# might not be necessary
df['forks']=None
# iterate the dataframe as follows:
'''
loop through dataframe
  pull repo
  build query
  run query
  update dataframe
'''
for row in df.itertuples():
    # only github for now as client is connected to github_events DB
    if row.forge == 'github':
        forks = 0
        repo = row.repo
        # skip the NaN repos
        if type(repo) == str:
            query = query_forks_L + '\''+repo+'\''
            forks = client.execute(query)
            # query returns a tuple of list elements accessible by [first list][first item]
            # no forks returns an empty list
            if not forks:
                df.at[row.Index, 'forks'] = 0
            else: df.at[row.Index, 'forks'] = forks[0][0]


# In[ ]:


# write update to 200_forks.csv
df.to_csv('200_forks.csv', encoding='utf-8', index=1)
df


# In[ ]:


# merge two csv files into one
# 1. 200_stars.csv
# 2. 200_forks.csv
#
# might prefer to append the new column? merge seems a bit cumbersome?
#
# has no index, CMC_id is in first column
dfs = pd.read_csv('200_stars.csv', index_col=0)
#dfsm = dfs[['stars']].copy()
dff = pd.read_csv('200_forks.csv', index_col=0)
#dffm = dff[['forks']].copy()
#


# In[ ]:


# 'CMC_id' is the key, however 'repo', and 'forge' are also merged
# to prevent duplicate columns
# -> might be uncecessary?
dfm = pd.merge(dfs,dff,on=['CMC_id','repo','forge'])


# In[ ]:


# write update to 200_merged.csv
dfm.to_csv('200_merged.csv', encoding='utf-8', index=1)


# In[91]:


# AUTHORS query:
# A most-recent three-month average 
# excluding current month because it is in progress
# modify for static clickhouse data which stops at 2020-12-07
# >>created_at >= dateSub(MONTH, 6,toStartOfMonth(now())) AND
# >>created_at < dateSub(MONTH, 3,toStartOfMonth(now()))
#
QUERY_AUTHORS = '''
SELECT
    ROUND( SUM(authors) / COUNT(month), 2) AS average
FROM
(
    SELECT 
        uniq(actor_login) AS authors,
        toMonth(created_at) AS month,
        toYear(created_at) AS year
    FROM github_events
    WHERE event_type IN ('PullRequestEvent', 'IssuesEvent', 'IssueCommentEvent', 'PullRequestReviewCommentEvent') AND
        repo_name = 'bitcoin/bitcoin' AND
        created_at >= dateSub(MONTH, 3,toStartOfMonth(now())) AND
        created_at < toStartOfMonth(now())
    GROUP BY month, year
    ORDER BY year DESC, month DESC
)'''
query_authors_L = '''
SELECT
    ROUND( SUM(authors) / COUNT(month), 2) AS average
FROM
(
    SELECT 
        uniq(actor_login) AS authors,
        toMonth(created_at) AS month,
        toYear(created_at) AS year
    FROM github_events
    WHERE event_type IN ('PullRequestEvent', 'IssuesEvent', 'IssueCommentEvent', 'PullRequestReviewCommentEvent') AND
        repo_name = 
'''
q_repo='bitcoin/bitcoin'
query_authors_R = '''AND
        /*created_at >= dateSub(MONTH, 3,toStartOfMonth(now())) AND
        created_at < toStartOfMonth(now())*/
        created_at >= dateSub(MONTH, 6,toStartOfMonth(now())) AND
        created_at < dateSub(MONTH, 3,toStartOfMonth(now()))
    GROUP BY month, year
    ORDER BY year DESC, month DESC
)'''
query_authors=query_authors_L + '\'' + q_repo + '\'' + query_authors_R


# In[99]:


# Read in 200_repos.csv
dfr = pd.read_csv('200_repos.csv', index_col=0)
# new df with only 2 columns
# 'CMC_id' as index is maintained
df = dfr[['repo','forge']].copy()
#dfs = df[0:20].copy()


# In[92]:


res=client.execute(QUERY_AUTHORS)
res


# In[ ]:


print(QUERY_AUTHORS)


# In[93]:


print(query_authors)


# In[101]:


for row in df.itertuples():
    # only github for now as client is connected to github_events DB
    if row.forge == 'github':
        #forks = 0
        repo = row.repo
        # skip the NaN repos
        if type(repo) == str:
            query = query_authors_L + '\'' + repo + '\'' + query_authors_R
            authors = client.execute(query)
            # query returns a tuple of list elements accessible by [first list][first item]
            # average of no authors returns a nan
            if math.isnan(result[0][0]):
                df.at[row.Index, 'authors'] = 0
            else: df.at[row.Index, 'authors'] = authors[0][0]


# In[ ]:





# In[104]:


# write update to 200_authors.csv
df.to_csv('200_authors.csv', encoding='utf-8', index=1)


# In[105]:


# update MERGED sheet with new data
# 'CMC_id' is the key, however 'repo', and 'forge' are also merged
# to prevent duplicate columns
df_temp = pd.read_csv('200_merged.csv', index_col=0)
dfm = pd.merge(df_temp,df,on=['CMC_id','repo','forge'])
dfm.to_csv('200_merged.csv', encoding='utf-8', index=1)


# In[106]:


print(client.execute('SELECT created_at FROM github_events ORDER by created_at DESC LIMIT 10'))


# In[161]:


# COMMITS query:
# A most-recent three-month average 
# excluding current month because it is in progress
#
# modify for static clickhouse data which stops at 2020-12-07:
# >>created_at >= dateSub(MONTH, 6,toStartOfMonth(now())) AND
# >>created_at < dateSub(MONTH, 3,toStartOfMonth(now()))
# 
# note: there will be moderate timezone discrepancies, especially 
#       when calculating near the first of the month
#
QUERY_COMMITS = '''
SELECT ROUND( SUM(sum_push_distinct) / COUNT(month), 2) AS average
FROM
(
    SELECT SUM(push_distinct_size) AS sum_push_distinct, 
        toMonth(created_at) AS month,
        toYear(created_at) AS year
    FROM github_events
    WHERE repo_name = 'bitcoin/bitcoin' AND 
        event_type = 'PushEvent' AND
        /*created_at >= dateSub(MONTH, 3,toStartOfMonth(now())) AND
        created_at < toStartOfMonth(now())*/
        created_at >= dateSub(MONTH, 7,toStartOfMonth(now())) AND
        created_at < dateSub(MONTH, 4,toStartOfMonth(now()))
    GROUP BY month, year
    ORDER BY year DESC, month DESC
)
'''
query_commits_L ='''
SELECT ROUND( SUM(sum_push_distinct) / COUNT(month), 2) AS average
FROM
(
    SELECT SUM(push_distinct_size) AS sum_push_distinct, 
        toMonth(created_at) AS month,
        toYear(created_at) AS year
    FROM github_events
    WHERE repo_name = 
'''
q_repo='bitcoin/bitcoin'
query_commits_R = '''
AND 
        event_type = 'PushEvent' AND
        /*created_at >= dateSub(MONTH, 3,toStartOfMonth(now())) AND
        created_at < toStartOfMonth(now())*/
        created_at >= dateSub(MONTH, 7,toStartOfMonth(now())) AND
        created_at < dateSub(MONTH, 4,toStartOfMonth(now()))
    GROUP BY month, year
    ORDER BY year DESC, month DESC
)
'''
query_commits=query_commits_L + '\'' + q_repo + '\'' + query_commits_R


# In[163]:


res=client.execute(query_commits)
res


# In[199]:


# Read in 200_repos.csv
dfr = pd.read_csv('200_repos.csv', index_col=0)
# new df with only 2 columns
# 'CMC_id' as index is maintained
df = dfr[['repo','forge']].copy()


# In[181]:


query_test_zero='''
SELECT ROUND( SUM(sum_push_distinct) / COUNT(month), 2) AS average
FROM
(
    SELECT SUM(push_distinct_size) AS sum_push_distinct, 
        toMonth(created_at) AS month,
        toYear(created_at) AS year
    FROM github_events
    WHERE repo_name = 'Uniswap/uniswap-v2-core' AND 
        event_type = 'PushEvent' AND
        /*created_at >= dateSub(MONTH, 3,toStartOfMonth(now())) AND
        created_at < toStartOfMonth(now())*/
        created_at >= dateSub(MONTH, 6,toStartOfMonth(now())) AND
        created_at < dateSub(MONTH, 3,toStartOfMonth(now()))
    GROUP BY month, year
    ORDER BY year DESC, month DESC
)'''
res=client.execute(query_test_zero)
res


# In[ ]:


import math
if math.isnan(res[0][0]): print('not')
else: print('dunno')


# In[200]:


for row in df.itertuples():
    # only github for now as client is connected to github_events DB
    if row.forge == 'github':
        #forks = 0
        repo = row.repo
        # skip the NaN repos
        if type(repo) == str:
            query = query_commits_L + '\'' + repo + '\'' + query_commits_R
            result = client.execute(query)
            # query returns a tuple of list elements accessible by [first list][first item]
            # average of no commits returns a nan
            if math.isnan(result[0][0]):
                df.at[row.Index, 'commits'] = 0
            else: df.at[row.Index, 'commits'] = result[0][0]


# In[202]:


# write update to 200_commits.csv
df.to_csv('200_commits.csv', encoding='utf-8', index=1)


# In[168]:


# update MERGED sheet with new data
# 'CMC_id' is the key, however 'repo', and 'forge' are also merged
# to prevent duplicate columns
df_temp = pd.read_csv('200_merged.csv', index_col=0)
dfm = pd.merge(df_temp,df,on=['CMC_id','repo','forge'])
dfm.to_csv('200_merged.csv', encoding='utf-8', index=1)


# In[207]:


# total COMMENTS includes all commenting activity
# any comments counts as activity and increase engagement
# there are 3 event_type comment events:
# >CommitCommentEvent
# >IssueCommentEvent
# >CommitCommentEvent
#
'''
/* View distribution of comments*/
SELECT 
    uniq(comment_id) AS total_comments,
    uniqIf(comment_id, event_type = 'PullRequestReviewCommentEvent') AS pr_comments,
    uniqIf(comment_id, event_type = 'IssueCommentEvent') AS issue_comments,
    uniqIf(comment_id, event_type = 'CommitCommentEvent') AS commit_comments,
    toMonth(created_at) AS month,
    toYear(created_at) AS year
FROM github_events
WHERE 
   repo_name = 'bitcoin/bitcoin' AND
   toYear(created_at) >= 2020
GROUP BY month, year
ORDER BY year DESC, month DESC
'''
# only Sept/Oct/Nov 2020 #
QUERY_COMMENTS='''
SELECT ROUND( SUM(total) / COUNT(month), 2) AS average
FROM
(
SELECT 
    (
        uniqIf(comment_id, event_type = 'PullRequestReviewCommentEvent')+
        uniqIf(comment_id, event_type = 'IssueCommentEvent')+
        uniqIf(comment_id, event_type = 'CommitCommentEvent') ) AS total,
    toMonth(created_at) AS month,
    toYear(created_at) AS year
FROM github_events
WHERE 
   repo_name = 'bitcoin/bitcoin' AND
   /*created_at >= dateSub(MONTH, 3,toStartOfMonth(now())) AND
   created_at < toStartOfMonth(now())*/
   created_at >= dateSub(MONTH, 7,toStartOfMonth(now())) AND
   created_at < dateSub(MONTH, 4,toStartOfMonth(now()))
GROUP BY month, year
ORDER BY year DESC, month DESC
)
'''
query_L='''
SELECT ROUND( SUM(total) / COUNT(month), 2) AS average
FROM
(
SELECT 
    (
        uniqIf(comment_id, event_type = 'PullRequestReviewCommentEvent')+
        uniqIf(comment_id, event_type = 'IssueCommentEvent')+
        uniqIf(comment_id, event_type = 'CommitCommentEvent') ) AS total,
    toMonth(created_at) AS month,
    toYear(created_at) AS year
FROM github_events
WHERE 
   repo_name = 
'''
query_R='''
AND
   /*created_at >= dateSub(MONTH, 3,toStartOfMonth(now())) AND
   created_at < toStartOfMonth(now())*/
   created_at >= dateSub(MONTH, 7,toStartOfMonth(now())) AND
   created_at < dateSub(MONTH, 4,toStartOfMonth(now()))
GROUP BY month, year
ORDER BY year DESC, month DESC
)
'''


# In[209]:


res=client.execute(QUERY_COMMENTS)
res


# In[212]:


#
query_L='''
SELECT ROUND( SUM(total) / COUNT(month), 2) AS average
FROM
(
SELECT 
    (
        uniqIf(comment_id, event_type = 'PullRequestReviewCommentEvent')+
        uniqIf(comment_id, event_type = 'IssueCommentEvent')+
        uniqIf(comment_id, event_type = 'CommitCommentEvent') ) AS total,
    toMonth(created_at) AS month,
    toYear(created_at) AS year
FROM github_events
WHERE 
   repo_name = 
'''
query_R='''
AND
   /*created_at >= dateSub(MONTH, 3,toStartOfMonth(now())) AND
   created_at < toStartOfMonth(now())*/
   created_at >= dateSub(MONTH, 7,toStartOfMonth(now())) AND
   created_at < dateSub(MONTH, 4,toStartOfMonth(now()))
GROUP BY month, year
ORDER BY year DESC, month DESC
)
'''
'''
@column name of the column to be added to the dataframe
@query_L
@query_R
@df dataframe
'''
def runQuery(column_name, query_L, query_R, df):
    for row in df.itertuples():
        # only github for now as client is connected to github_events DB
        if row.forge == 'github':
            repo = row.repo
            # skip the NaN repos
            if type(repo) == str:
                query = query_L + '\'' + repo + '\'' + query_R
                result = client.execute(query)
                # query returns a tuple of list elements accessible by [first list][first item]
                # average of zero returns a nan
                if math.isnan(result[0][0]):
                    df.at[row.Index, column_name] = 0
                else: df.at[row.Index, column_name] = result[0][0]
    return 'dataframe updated'


# In[213]:


# Read in 200_repos.csv
dfr = pd.read_csv('200_repos.csv', index_col=0)
# new df with only 2 columns
# 'CMC_id' as index is maintained
df = dfr[['repo','forge']].copy()


# In[217]:


runQuery('comments',query_L,query_R,df)


# In[220]:


# update MERGED sheet with new data
# 'CMC_id' is the key, however 'repo', and 'forge' are also merged
# to prevent duplicate columns
df_temp = pd.read_csv('200_merged.csv', index_col=0)
dfm = pd.merge(df_temp,df,on=['CMC_id','repo','forge'])
dfm.to_csv('200_merged.csv', encoding='utf-8', index=1)


# In[224]:


# view all PR activity sorted into: opened, closed, reopened
'''
SELECT  COUNT() AS total,
    SUM(action = 'opened') AS opened,
    SUM(action = 'closed') AS closed,
    SUM(action = 'reopened') AS reopened,
    toYear(created_at) AS year, 
    toMonth(created_at) AS month
FROM github_events
WHERE repo_name = 'bitcoin/bitcoin' AND 
    toYear(created_at) >= '2019' AND 
    event_type = 'PullRequestEvent'
GROUP BY month, year
ORDER BY year DESC, month DESC
'''
'''
SELECT
    ROUND( SUM(opened) / COUNT(month), 2) AS average
FROM
(
    SELECT  
        SUM(action = 'opened') AS opened,
        toYear(created_at) AS year, 
        toMonth(created_at) AS month
    FROM github_events
    WHERE repo_name = 'bitcoin/bitcoin' AND 
        event_type = 'PullRequestEvent' AND 
        created_at >= dateSub(MONTH, 7,toStartOfMonth(now())) AND
        created_at < dateSub(MONTH, 4,toStartOfMonth(now()))
    GROUP BY month, year
    ORDER BY year DESC, month DESC
)
'''
query_L='''
SELECT
    ROUND( SUM(opened) / COUNT(month), 2) AS average
FROM
(
    SELECT  
        SUM(action = 'opened') AS opened,
        toYear(created_at) AS year, 
        toMonth(created_at) AS month
    FROM github_events
    WHERE repo_name = 
'''
query_R='''
AND 
        event_type = 'PullRequestEvent' AND 
        created_at >= dateSub(MONTH, 7,toStartOfMonth(now())) AND
        created_at < dateSub(MONTH, 4,toStartOfMonth(now()))
    GROUP BY month, year
    ORDER BY year DESC, month DESC
)
'''


# In[225]:


# Read in 200_repos.csv
dfr = pd.read_csv('200_repos.csv', index_col=0)
# new df with only 2 columns
# 'CMC_id' as index is maintained
df = dfr[['repo','forge']].copy()
runQuery('PR_open',query_L,query_R,df)


# In[226]:


# update MERGED sheet with new data
# 'CMC_id' is the key, however 'repo', and 'forge' are also merged
# to prevent duplicate columns
df_temp = pd.read_csv('200_merged.csv', index_col=0)
dfm = pd.merge(df_temp,df,on=['CMC_id','repo','forge'])
dfm.to_csv('200_merged.csv', encoding='utf-8', index=1)


# In[227]:


dfm


# In[234]:


import sys,time
#criticality (again)
# >>>>!!!!
# minor problem here with ETC double-IDs...
# !!!!>>>>
# Read in 200_repos.csv
dfr = pd.read_csv('200_repos.csv', index_col=0)
# new df with only 2 columns
# 'CMC_id' as index is maintained
df = dfr[['source_code','forge']].copy()
dfc = pd.read_csv('Project_Criticality_all.csv')
for row in df.itertuples():
  # only search for strings; floats (NaN) are skipped
  if isinstance(row.source_code, str):
    url = str(row.source_code)
    # loop through df2 (criticality) looking for source code url
    for row2 in dfc.itertuples():
      if url == row2.url:
        df.at[row.Index, 'citicality'] = row2.criticality_score
        break
    sys.stdout.write(".")
    sys.stdout.flush()


# In[246]:


# update MERGED sheet with new data
# 'CMC_id' is the key, however 'repo', and 'forge' are also merged
# to prevent duplicate columns
df.drop(columns=['source_code'], inplace=True)
df_temp = pd.read_csv('200_merged.csv', index_col=0)
dfm = pd.merge(df_temp,df,on=['CMC_id','forge'])
dfm.to_csv('200_merged.csv', encoding='utf-8', index=1)


# In[ ]:




