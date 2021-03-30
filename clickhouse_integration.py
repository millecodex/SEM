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


# In[3]:


from sqlalchemy import create_engine
from clickhouse_driver import Client

# dependencies
# >ipython-sql
# install by command prompt:
# >conda install -yc conda-forge ipython-sql


# In[4]:


client = Client('localhost')


# In[3]:


get_ipython().run_line_magic('load_ext', 'sql')


# In[ ]:


result = client.execute('SELECT now(), version()')


# In[ ]:


print(result)


# In[ ]:


result = client.execute('SELECT now(), version()')
print("RESULT: {0}: {1}".format(type(result), result))
for t in result:
    print(" ROW: {0}: {1}".format(type(t), t))
    for v in t:
        print("  COLUMN: {0}: {1}".format(type(v), v))


# In[ ]:


print(client.execute('SHOW TABLES'))


# In[ ]:


query = '''
SELECT
    repo_name,
    count()
FROM github_events
WHERE (event_type = 'WatchEvent') AND (repo_name LIKE '%_/_%')
GROUP BY repo_name
ORDER BY length(repo_name) ASC
LIMIT 11
'''


# In[ ]:


# load CSV file into dataframe
# get test dataframe with different repos
#  loop through dataframe
#   pull repo
#   build query
#   run query
#   write to dataframe


# In[8]:


import pandas as pd
# not yet needed here
import time
import math


# In[35]:


# Read CSV file into DataFrame df
# 200_repos_ready.csv has no index, CMC_id is in first column
# NaN is assigned to empty cells
dfs = pd.read_csv('200_repos.csv', index_col=0)


# In[36]:


df = dfs[['repo','forge']].copy()


# In[106]:


# subset dataframes for testing
# use .copy() as slicing will not allow for assignment
df10 = df.iloc[:10].copy()
df33 = df.iloc[:33].copy()


# In[38]:


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


# In[124]:


query = '''
SELECT 
    count() 
FROM github_events 
WHERE event_type = 'WatchEvent' 
    AND repo_name =
'binance-chain/bsc'
GROUP BY action
'''


# In[127]:


query2 = '''
SELECT 
    count() 
FROM github_events 
WHERE event_type = 'WatchEvent' 
    AND repo_name =
'HuobiGroup/huobi-eco-chain'
GROUP BY action
'''


# In[125]:


print(query)


# In[130]:


res=client.execute(query)
res2=client.execute(query2)
print(res)
print(res2)


# In[139]:


if not res2: print('not')


# In[39]:


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
                continue
            else: df.at[row.Index, 'stars'] = stars[0][0]


# In[40]:


# write update to 200_copy_stars.csv
# note beginning of script: pd.read_csv('200_repos_ready.csv', index_col=0)
df.to_csv('200_stars.csv', encoding='utf-8', index=1)
df


# In[28]:


# Read in 200_repos.csv 
# has no index, CMC_id is in first column
dfr = pd.read_csv('200_repos.csv', index_col=0)
# new df with only 2 columns
# 'CMC_id' as index is maintained
df = dfr[['repo','forge']].copy()


# In[14]:


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


# In[15]:


result=client.execute(query_forks)
print(result)


# In[30]:


# initialize new column to null/None
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
            # no stars returns an empty list
            if not forks:
                continue
            else: df.at[row.Index, 'forks'] = forks[0][0]


# In[32]:


# write update to 200_forks.csv
df.to_csv('200_forks.csv', encoding='utf-8', index=1)
df


# In[62]:


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


# In[75]:


dfm = pd.merge(dfs,dff,on=['CMC_id','repo','forge'])


# In[76]:


# write update to 200_merged.csv
dfm.to_csv('200_merged.csv', encoding='utf-8', index=1)


# In[ ]:




