"""
----------------------------------------------
I.  Update CMC info from the API
----------------------------------------------
 1. get top 200 info from CMC
         [CMC_id, name, rank, ticker, Source_code]
 2. get top 200 website info
         [primary_web, secondary_web]
 3. merge the two dataframes as 'dfnew'
 4. write 'cmc_top_200.csv'
----------------------------------------------
II. Merge with manually updated Source Code info
----------------------------------------------
 4. read 'cmc_data_200_man.csv'
 5. merge together new ['Source_code'] with 
    manually updated ['source_code']
 6. write 'cmc_data_200_man_update.csv'
 7. <future work> check for duplicates?
----------------------------------------------
III. Send to prepare_repos.py to get forge & repo
---------------------------------------------- 
"""
# This script will contact CoinMarketCap's API to gather info about cryptocurrency projects
# 
# It will merge two calls to create a dataframe/csv listing project's:
#  <id>, <rank>, <ticker>, <name>, & <source code location>
# 
# You must have a coinmarketcap dev key to use their API
#
import pandas as pd 
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

# listing of top 200 (per 1 credit) by market cap
# default sort is by market cap
# see: https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyListingsLatest
# this will fetch 200 at a time
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {
    'start':'1',
    'limit':'200',
    'convert':'USD'
}
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': 'xxx',
}

session = Session()
session.headers.update(headers)

try:
    response = session.get(url, params=parameters)
    data_listing = json.loads(response.text)
except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)



# extract data fields; could be more efficient
# access CMC_ID field 
# access NAME field 
# access SYMBOL (ticker) field 
# access RANK field 
cmc_id = []
name = []
ticker = []
cmc_rank = []
for project in data_listing['data']:
    cmc_id.append(project['id'])  
    name.append(project['name'])
    ticker.append(project['symbol'])
    cmc_rank.append(project['cmc_rank'])


# create a string of IDs to pass to the API
IDString = ''
for id in cmc_id:
    IDString = IDString + str(id) +','
IDString = IDString[:-1]
#print(IDString)

#testIDString=''
#for id in testID:
#    testIDString = testIDString + str(id) +','
#testIDString = testIDString[:-1]
#print(testIDString)


# get JSON listing of metadata
# see: https://coinmarketcap.com/api/documentation/v1/#operation/getV2CryptocurrencyInfo
# 1 credit per 100 cryptocurrencies (rounded up)
# pass a string of IDs, slugs, or symbols (tickers)
url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'
parameters = {
    'id':IDString,
}
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': 'xxx',
}
session = Session()
session.headers.update(headers)

try:
    response = session.get(url, params=parameters)
    metadata = json.loads(response.text)
except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)


# ----S O U R C E   C O D E-------------------------------
# access date::<key>::urls::sourcecode field
# json order is not preserved so build an array containing:
# [ [id, sourcecode], [id,sourcecode],...,[id,sourcecode]]
# where id is CMC unique id
source = []
for project in metadata['data']:
    id = project
    sc = metadata['data'][id]['urls']['source_code']
    # turn the sc list into a string and trim the ['']
    element = [id,str(sc)[2:-2]]
    source.append(element)

# create dataframe from this list so it can be merged 
dfsource = pd.DataFrame(data=source,columns=['CMC_id','Source_code'])

df = pd.DataFrame({'CMC_id':cmc_id}) 
# add columns, probably a more elegant way to do this
df['CMC_rank'] = cmc_rank
df['name'] = name
df['ticker'] = ticker

# DF is an INT type and DFSOURCE is a STRING type, cast df as string to merge
# df.astype(str)
dfout = pd.merge(df.astype(str),dfsource, on=['CMC_id'])


# write to a CSV for doing other stuffs
# if using COLAB 
'''
must authenticate first with google drive
from google.colab import drive
drive.mount('drive')
'''

# write the dataframe to CSV and copy to drive/directory
# >dfout.to_csv('CMCdata.csv', sep='\t', encoding='utf-8')
# >!cp CMCdata.csv "drive/My Drive/PhDstuffs"

# ----W E B S I T E--------------------------------------
# access date::<key>::urls::sourcecode field
# json order is not preserved so build an array containing:
# [ [id, website],...,[id, website]]
# where id is CMC unique id
site = []
for project in metadata['data']:
    id = project
    web = metadata['data'][id]['urls']['website']
    # turn the list into a string and trim the ['']
    #print(sc)
    element = [id,str(web)[1:-1]]
    site.append(element)

# create dataframe from this list so it can be merged 
dfweb = pd.DataFrame(data = site, columns = ['CMC_id','website'])


# some listings have muliple sites
# split into primary and secondary sites
# first instance is web_primary
# if second is web_secondary
dfweb = pd.concat([dfweb[['CMC_id']], dfweb['website'].str.split(', ', expand=True)], axis=1)
dfweb.rename(columns = {0:'web_primary',1:'web_secondary'}, inplace = True)
# remove single quotes
dfweb['web_primary'].replace("[\']", "", inplace=True, regex=True)
dfweb['web_secondary'].replace("[\']", "", inplace=True, regex=True)


# output to '200_websites.csv'; key is 'CMC_id'
dfweb.to_csv('200_websites.csv', encoding='utf-8', index=False)


# Read in cmc_data_200_man.csv if not running notebook from beginning
#dfman = pd.read_csv('cmc_data_200_man.csv')
# Read in 200_websites.csv if not running notebook from beginning
#dfweb = pd.read_csv('200_websites.csv', index_col=0)

#dfout=pd.merge(df.astype(str),dfsource, on=['CMC_id'])
dfnew = pd.merge(dfout,dfweb, on=['CMC_id'], how = 'outer')

# output to 'cmc_top_200.csv'; key is 'CMC_id'
dfnew.to_csv('cmc_top_200.csv', encoding='utf-8', index=False)

# update the types; makes for easier comparison
dfnew['CMC_id'] = dfnew['CMC_id'].astype('int')
dfnew['CMC_rank'] = dfnew['CMC_rank'].astype('int')
#dfnew.info()

dfman = pd.read_csv('cmc_data_200_man.csv')
dfman.drop(['CMC_rank'], axis = 1, inplace = True)

# merge the two together; keep common columns
dfm = pd.merge(dfnew,dfman, on = ['CMC_id','name','ticker','web_primary','web_secondary'], how = 'outer')

# update source_code (lowercase)
for row in dfm.itertuples():
    if row.check_source != 'y':
        
        # copy new repo location to 'source_code'
        dfm.at[row.Index, 'source_code'] = row.Source_code
        
        # update the 'check_source' entry for manual verification
        dfm.at[row.Index, 'check_source'] = 'n'

dfm.drop(['Source_code'], axis = 1, inplace = True)

# output to 'cmc_data_200_man_update.csv';
dfm.to_csv('cmc_data_200_man_update.csv', encoding='utf-8', index=False)

