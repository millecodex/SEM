'''
P R E P A R E   R E P O S
This starts with 'cmc_data_200_man.csv' has been manually 
updated and merged and extracts the forge and repo information.

Prerequisite:
>> CMC_API.py
 1. Manually updated source code repos in cmc_data_200_man.csv
 2. fetch top 200 from CMC and merge
>> 
'''
import pandas as pd

# Read CSV file into DataFrame df
# double check this index
df = pd.read_csv('cmc_data_200_man.csv')


# pandas imports empty cells as NaN, 
# and displays empty Object types as None
#
#
# check 'source_code' column for tailing forwardslash & remove
def removeSlash(string):
    # type check
    if type(string) == str:
        # trim slash
        if string[-1] == '/':
            return string[:-1]
        else:
            return string
    else:
        return None
        
# findRepo takes the SourceCode string and strips the domain
# this can be useful for querying GitHub databases
def findRepo(string):
    # type check
    if type(string) == str:
        if string.find('github') > 0 or string.find('gitlab') > 0:
            return string[19:]
        elif string.find('bitbucket') > 0:
            return string[22:]
        elif string == 'private':
            return None
        else:
            # presumably some other URL
            return string[8:]
    # catch non-str types
    else:
        return None

# extract the host from the SourceCode string
# only really interested in GitHub (and GitLab)
# data cannot be obtained from private or missing Forges
def findForge(string):
    # type check
    if type(string) == str:
        if string.find('github') > 0:
            return 'github'
        elif string.find('gitlab') > 0:
            return 'gitlab'
        elif string.find('bitbucket') > 0:
            return 'bitbucket'
        elif string == 'private':
            return None
    # catch non-str types
    else:
        return None



# strings for testing
s1 = 'https://github.com/bitcoin/bitcoin'
s2 = 'private'
s3 = 'https://cardanoupdates.com/'
s4 = 'https://github.com/WrappedBTC/bitcoin-token-smart-contracts'
s5 = 'https://gitlab.com/NebulousLabs/Sia'
s6
s7 = ''
s8 = 'https://bitbucket.com/chromawallet'
findForge(s6)


# check 'source_code' column for tailing forwardslash & remove 
df['source_code'] = df['source_code'].apply(removeSlash)

# extract repo and forge info into new columns
df['repo'] = df['source_code'].apply(findRepo)
df['forge'] = df['source_code'].apply(findForge)


# write out to '200_repos.csv'
# ['source_code'] column is used by clickhouse to run queries
df.to_csv('200_repos.csv', encoding = 'utf-8', index = False)