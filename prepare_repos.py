'''
P R E P A R E   R E P O S
This starts with the CSV from coin market cap that has been manually 
updated for source code repositories and extracts the forge and repo 
information.
The udpated dataframe is written out as a csv as an intermdiate backup
step.
'''
import pandas as pd
# not yet needed here
import time
import math

# Read CSV file into DataFrame df
df = pd.read_csv('CMCdata_200.csv', index_col=0)

# subset dataframes for testing
# use .copy() as slicing will not allow for assignment
dfss = df.iloc[:10].copy()
dfs = df.iloc[100:150].copy()

# check 'source_code' column for tailing forwardslash & remove
def findSlash(string):
    # type check
    if type(string) == str:
        # trim slash
        if string[-1] == '/':
            return string[:-1]
        else:
            return string
    else:
        return 'none'
        
# findRepo takes the SourceCode string and strips the domain
# this can be useful for querying GitHub databases
# pandas imports empty cells as NaN, must type check this
def findRepo(string):
    # type check
    if type(string) == str:
        if string.find('github') > 0 or string.find('gitlab') > 0:
            return string[19:]
        elif string.find('bitbucket') > 0:
            return string[22:]
        elif string=='private':
            return ''
        else:
            # presumably some other URL
            return string[8:]
    # catch non-str types
    else:
        return 'none'

# extract the host from the SourceCode string
# only really interested in GitHub and GitLab
# data cannot be obtained from private or missing Forges
# pandas imports empty cells as NaN, must type check this
def findForge(string):
  # type check
  if type(string) == float:
    return 'none'
  elif string.find('github') > 0:
    return 'github'
  elif string.find('gitlab') > 0:
    return 'gitlab'
  elif string.find('bitbucket') > 0:
    return 'bitbucket'
  elif string=='private':
    return string
  else:
    return 'other'

# strings for testing
s1='https://github.com/bitcoin/bitcoin'
s2='private'
s3='https://cardanoupdates.com/'
s4='https://github.com/WrappedBTC/bitcoin-token-smart-contracts'
s5='https://gitlab.com/NebulousLabs/Sia'
s6
s7=''
s8='https://bitbucket.com/chromawallet'
findForge(s6)

# check 'source_code' column for tailing forwardslash & remove
df['source_code']=df['source_code'].apply(findSlash)
# extract repo and forge info into new columns
df['repo']=df['source_code'].apply(findRepo)
df['forge']=df['source_code'].apply(findForge)

# write back to new csv
# not sure if I need encoding parameter
# note that pd.read_csv('CMCdata_200.csv', index_col=0) has index
df.to_csv('200_repos_ready.csv', encoding='utf-8', index=False)

