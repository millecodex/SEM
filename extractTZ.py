#notes:
# web tutorial: https://chaoss.github.io/grimoirelab-tutorial/perceval/git.html
# command line: 
# !pip3 install grimoirelab
# !perceval git 'https://github.com/bitcoin/bitcoin.git' --from-date '2021-07-14'
#
#
#! /usr/bin/env python3
from perceval.backends.core.git import Git
import datetime
import dateutil.rrule
import dateutil.tz

# url for the git repo to analyze
repo_url1 = 'http://github.com/grimoirelab/perceval.git'
repo_url2 = 'https://github.com/bitcoin/bitcoin.git'
repo_url3 = 'https://github.com/ethereum/go-ethereum.git'
repo_url4 = 'https://github.com/input-output-hk/cardano-node.git'
repo_url5 = 'https://github.com/paritytech/polkadot.git'
repo_url6 = 'https://github.com/ripple/rippled.git'
repo_url7 = 'https://github.com/Uniswap/uniswap-v2-core.git'
repo_url8 = 'https://github.com/smartcontractkit/chainlink.git'
# directory for letting Perceval clone the git repo
# must be unique for the repo because it is reused
repo_dir = '/tmp/link.git'

# create a Git object, pointing to repo_url, using repo_dir for cloning
repo = Git(uri=repo_url8, gitpath=repo_dir)
# fetch all commits as an iteratoir, and iterate it printing each hash
count = 0
#fromDate = datetime.datetime(2021, 7, 14, 0, 0, 0,tzinfo=dateutil.tz.tzutc())
fromDate = datetime.datetime(2021, 7, 13)
toDate = datetime.datetime(2021, 7, 14)

count = 0
for commit in repo.fetch(from_date=fromDate,to_date=toDate):
    count += 1
    # commit date is a string
    # print(commit['data']['CommitDate'])
    time1 = commit['data']['CommitDate']

    # unfortunately this strips the timezone... not what i'm after
    dateTimeObject = datetime.datetime.strptime(' '.join(time1.split(' ')[:-1]), '%a %b %d %H:%M:%S %Y')
    #print('\n')
    if count > 0:
        break
print(count)
print(dateTimeObject)

