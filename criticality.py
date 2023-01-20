#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import sys
import time
import math
import json
import pandas as pd


# In[ ]:


# #--------------------------------------------------------------
# #-- S E A R C H   C R I T I C A L I T Y   S P R E A D S H E E T
# #--------------------------------------------------------------
# # using the csv file of CRITICALITY_SCORE and searching for 
# # repos from 200_repos; this excludes new/current projects
# # download: https://storage.cloud.google.com/ossf-criticality-score
# # UDPATE: looks like a monthly run is published here (wish I had of known!)
# #--------------------------------------------------------------
# # Read '200_repos.csv' into DataFrame df
# #
# # NaN is assigned to empty cells
# df = pd.read_csv('200_repos.csv')
# dfs = df[['CMC_id', 'source_code', 'forge']].copy()
# dfc = pd.read_csv('project_criticality_all.csv')
# num = 0
# for row in dfs.itertuples():
#     # only search if github
#     if row.forge == 'github':
#         # only search for strings; floats (NaN) are skipped
#         if isinstance(row.source_code, str):
#             url = str(row.source_code)
#             # loop through df2 (criticality) looking for source code url
#             for row2 in dfc.itertuples():
#                 if url == row2.url:
#                     dfs.at[row.Index, 'criticality'] = row2.criticality_score
#                     num += 1
#                     break
#             sys.stdout.write(".")
#             sys.stdout.flush()
# print(str(num), 'criticality scores found and updated')

# # update MERGED sheet with new data
# # 'CMC_id' is the key, drop 'repo', and 'forge' before the merge
# # to prevent duplicate columns
# dfs.drop(columns = ['source_code', 'forge'], inplace = True)
# dfm = pd.merge(df,dfs,on = ['CMC_id'], how = 'outer')

# # write out new data
# dfs.to_csv('200_crit.csv', encoding='utf-8', index = 0)
# dfm.to_csv('200_merged.csv', encoding='utf-8', index = 0)


# In[ ]:


#-------------------------------------------------
# -- C A L L   C R I T I C A L I T Y _ S C O R E--
# require github token and command line access----
#-------------------------------------------------
#
# Input:
# 'cmc_repos_forge.csv' from prepare_repos.ipynb
#
# Outputs:
# 'crit_output_all.csv' contains all the info; see sample output below
# 'crit_only.csv' contains two columns: 'url:','criticality_score:'
#
# >> repo: https://github.com/ossf/criticality_score
# 0. make sure github access token is exported to PATH (see methodology notes)
# 1. install: pip3 install criticality-score
# 2. check PATH: WARNING: The script criticality_score is installed in '/home/user/.local/bin' which is not on PATH.
# >> export PATH="/home/user/.local/bin:$PATH"
# 3. get 'GITHUB_AUTH_TOKEN' and export path on command line or set env variable in jupyter
# 
# Set the environment variable 'GITHUB_AUTH_TOKEN' from Jupyter
# (this is a short-cut; in the future look into pycrosskit)
# >key = 'GITHUB_AUTH_TOKEN'
# >os.environ[key] = 'secret'
#
# read out the value
# >value = os.getenv(key)
# >print("Value of 'GITHUB_AUTH_TOKEN' environment variable :", value) 
#
# 4. run: criticality_score --repo https://github.com/bitcoin/bitcoin
# >sample output:
# '''     
# ['name: bitcoin',
#  'url: https://github.com/bitcoin/bitcoin',
#  'language: C++',
#  'created_since: 142',
#  'updated_since: 0',
#  'contributor_count: 961',
#  'org_count: 4',
#  'commit_frequency: 54.8',
#  'recent_releases_count: 3',
#  'updated_issues_count: 1920',
#  'closed_issues_count: 1467',
#  'comment_frequency: 2.7',
#  'dependents_count: 348588',
#  'criticality_score: 0.86651']
# '''


# In[2]:


key = 'GITHUB_AUTH_TOKEN'
os.environ[key] = 'xxx'


# In[3]:


value = os.getenv(key)
print("Value of 'GITHUB_AUTH_TOKEN' environment variable :", value) 


# In[37]:


# Read '200_repos.csv' into DataFrame df
#df = pd.read_csv('cmc_repos_forge.csv')
df = pd.read_csv('merged_Jan_2023.csv')
# keep 'source_code' location and 'forge'
df_in = df[['source_code', 'forge', 'language:']].copy()
df_in = df_in.rename(columns={'language:': 'language'})
# subset dataframes for testing
df_test1 = df_in.iloc[99:104].copy()
df_test2 = df_in.iloc[:20].copy()
df_test3 = df_in.iloc[99:104].copy()


# In[39]:


df200 = df_in.iloc[:199].copy()
df400 = df_in.iloc[200:399].copy()
df600 = df_in.iloc[400:].copy()


# In[7]:


# ------------------------------------------------
# dfParse builds a dataFrame using bash output
#  @output the command line output from calling criticality_score
#  @firstTime boolean to initialize the dataframe the first loop call
#  @dataframe the dataframe to be updated and returned
# ------------------------------------------------
def dfParse(output, firstUpdate, dataframe):
    jout = json.dumps(output)    #jout is a str
    out_dict = json.loads(jout)   #out_dict is a list
    
    # catch a possible traceback
    if 'Traceback' in out_dict[0]:
        print('found traceback')
        return dataframe
    
    # prepare the dataFrame, initialize with column headers the same
    # as the criticality_score output
    df = pd.DataFrame(out_dict)
    df.rename(columns = {0:'metric'}, inplace = True)
    df[['metric','value']] = df.metric.str.split(expand = True)
    df = df.transpose(copy = True)

    # remove index column (with labels 'metric' & 'value')
    # and reset the index
    df.reset_index(drop=True, inplace=True)

    # rename columns according to first row; then drop the row
    df = df.rename(columns = df.iloc[0]).drop(df.index[0])

    if firstUpdate:
        dataframe = df.copy()
    else:
        # append row[1] to df
        dataframe = dataframe.append(df, ignore_index = True)   
        
    return dataframe


# In[ ]:


# ------------------------------------------------------
# main loop requires dataFrame: 'df_in'
#                      returns: 'df_out'
# df_out does not have CMC_id and some will be missed;
# should be able to merge back on 'url:'=='source_code'
# ------------------------------------------------------
# This takes a while, criticality_score has a built-in
# rate limiter for handling github API limits. It still 
# gets stuck over about 200 url requests.
# for example:
# >Rate limit exceeded, sleeping till reset: 334 seconds.
# ------------------------------------------------------
# Sample Output:
#  223 total projects evaluated
#  153 criticality scores updated
#  70 repos private or missing
#  Total time elapsed: 22.6 minutes
# ------------------------------------------------------

# Need to chunk this better to avoid the rate limiting and
# its confusing with 200/400/600, etc.
#df_in = df200.copy()
#df_in = df400.copy()
df_in = df600.copy()
# df_in = df_test3.copy()

start = time.time()
total = 0
updated = 0
firstUpdate = True
df_out = pd.DataFrame

for row in df_in.itertuples():
    # proceed if github and source_code is a string and not private
    # added check 'and (pd.isna(row.language))' to update criticality columns Jan.2023, remove for future use
    if (row.forge == 'github') and isinstance(row.source_code, str) and (row.source_code != 'private') and (pd.isna(row.language)):
        cmd = 'criticality_score --repo ' + row.source_code
        print(row.source_code)
        output = get_ipython().getoutput('{cmd}')
        # if first element is ['name':'bitcoin'], output is as expected, can parse
        if 'name' in output[0]: 
            df_out = dfParse(output, firstUpdate, df_out)
            firstUpdate = False
            updated += 1
    total += 1
    sys.stdout.write(".")
    sys.stdout.flush()
    
# log some output with a timer
print('\n',str(df_in.shape[0]), 'total projects evaluated\n', 
      str(updated), 'criticality scores updated\n', 
      str(total - updated), 'repos private or missing\n', 
      'Total time elapsed:', round((time.time() - start)/60, 1), 'minutes')

#df200 = df_out.copy()
#df400 = df_out.copy()
df600 = df_out.copy()


# In[50]:


# write out new data
df200.to_csv('crit_output_200_Jan2023.csv', encoding='utf-8', index = 0)
df400.to_csv('crit_output_400_Jan2023.csv', encoding='utf-8', index = 0)
df600.to_csv('crit_output_600_Jan2023.csv', encoding='utf-8', index = 0)
# dft = df_out[['url:','criticality_score:']].copy()
# dft.to_csv('crit_only.csv', encoding='utf-8', index = 0)


# In[ ]:


# read in chunked data
# df200 = pd.read_csv('crit_output_all_0-200.csv')
# df400 = pd.read_csv('crit_output_all_200-400.csv')
# df600 = pd.read_csv('crit_output_all_400-600.csv')
# dfcrit200 = pd.read_csv('crit_only_0-200.csv')
# dfcrit400 = pd.read_csv('crit_only_200-400.csv')
# dfcrit600 = pd.read_csv('crit_only_400-600.csv')
df200 = pd.read_csv('crit_output_all_200.csv')


# In[46]:


# merge data frames
dfall = pd.concat([df200, df400, df600], ignore_index=True)
# dfcrit = pd.concat([dfcrit200, dfcrit400, dfcrit600], ignore_index=True)


# In[48]:


# write out merged frames
dfall.to_csv('crit_output_Jan2023.csv', encoding='utf-8', index = 0)
# dfcrit.to_csv('crit_only.csv', encoding='utf-8', index = 0)


# In[89]:


# merge criticality with cmc_repos_forge
#cmc_repos_forge = pd.read_csv(r"/home/japple/localDev/health/cmc/cmc_repos_forge.csv")

original = pd.read_csv('merged_Jan_2023.csv')


# In[ ]:


# [crit_output_all] 'url:' == [cmc_repos_forge] 'source_code'
dfall.drop(columns = ['name:'], inplace = True)


# In[ ]:


# rename [crit_output_all] 'url:' to 'source_code' to match
dfall.rename(columns = {'url:':'source_code'}, inplace = True)


# In[49]:


dfm = pd.merge(original, dfall, on = ['source_code'], how = 'outer')
#dfm.sort_values(by='CMC_rank', ascending=False)
#dfm.to_csv('merged_Jan2023.csv', encoding='utf-8', index=True)


# In[90]:


# loop to update criticality gaps
original['source_code'] = original['source_code'].str.lower()
dfall['source_code'] = dfall['source_code'].str.lower()
for i, row in original.iterrows():
    if row['source_code'] in dfall['source_code'].values:
        dfall_row = dfall.loc[dfall['source_code'] == row['source_code']]
        original.loc[i, 'language:'] = dfall_row['language:'].values[0]
        original.loc[i, 'created_since:'] = dfall_row['created_since:'].values[0]
        original.loc[i, 'updated_since:'] = dfall_row['updated_since:'].values[0]
        original.loc[i, 'contributor_count:'] = dfall_row['contributor_count:'].values[0]
        original.loc[i, 'org_count:'] = dfall_row['org_count:'].values[0]
        original.loc[i, 'commit_frequency:'] = dfall_row['commit_frequency:'].values[0]
        original.loc[i, 'recent_releases_count:'] = dfall_row['recent_releases_count:'].values[0]
        original.loc[i, 'updated_issues_count:'] = dfall_row['updated_issues_count:'].values[0]
        original.loc[i, 'closed_issues_count:'] = dfall_row['closed_issues_count:'].values[0]
        original.loc[i, 'comment_frequency:'] = dfall_row['comment_frequency:'].values[0]
        original.loc[i, 'dependents_count:'] = dfall_row['dependents_count:'].values[0]
        original.loc[i, 'criticality_score:'] = dfall_row['criticality_score:'].values[0]


# In[92]:


original.to_csv('crit_updated_Jan2023.csv', encoding='utf-8', index=True)


# In[ ]:


# merge alexa with merged_checked_manually
dfalexa = pd.read_csv(r"/home/japple/localDev/health/webRank/alexa.csv")
dfsource = pd.read_csv("merged_checked_manually.csv")
# merge on CMC_id
dft=dfalexa[['CMC_id', 'alexa_rank']].copy()


# In[ ]:


dfm=pd.merge(dfsource,dft,on=['CMC_id'], how='outer')
dfm.sort_values(by='CMC_rank', ascending=False)


# In[96]:


# ------------------------------------------------------------
# --C H E C K   F O R   D U P L I C A T E S-------------------
# CMC_id column *may* contain duplicate entries (CAKE, FUN!?)
# ------------------------------------------------------------
if dfm[dfm.duplicated(['CMC_id'], keep='last')].empty:
    print('No duplicate CMC_ids were found')
else: 
    num = len(dfm[dfm.duplicated(['CMC_id'], keep='last')])
    print(num, 'duplicates were found and deleted based on CMC_id:')
    print(dfm[dfm.duplicated(['CMC_id'], keep='last')])
    
    # delete duplicates keeping 2nd entry
    dfm.drop_duplicates(subset=['CMC_id'], keep='last', inplace=True)


# In[95]:


dfm.to_csv('merged.csv', encoding='utf-8', index=False)


# In[ ]:


# # store a dataframe in the kernel
# %store dfm

# # retrieve a datafram
# %store -r dfm

