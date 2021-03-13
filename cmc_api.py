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
cmc_id=[]
name=[]
ticker=[]
cmc_rank=[]
for project in data_listing['data']:
  cmc_id.append(project['id'])  
  name.append(project['name'])
  ticker.append(project['symbol'])
  cmc_rank.append(project['cmc_rank'])

# trim the lists for testing
testID=cmc_id[0:15]
testName=name[0:15]
testTicker=ticker[0:15]
testRank=cmc_rank[0:15]

# create a string of IDs to pass to the API
IDString=''
for id in cmc_id:
    IDString = IDString + str(id) +','
IDString = IDString[:-1]
print(IDString)

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

# access date::<key>::urls::sourcecode field
# json order is not preserved so build an array containing:
# [ [id, sourcecode], [id,sourcecode],...,[id,sourcecode]]
# where id is CMC unique id
source=[]
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
df['CMC_rank']=cmc_rank
df['name']=name
df['ticker']=ticker

# DF is an INT type and DFSOURCE is a STRING type, cast df as string to merge
# df.astype(str)
df_out=pd.merge(df.astype(str),dfsource, on=['CMC_id'])

# write to a CSV for doing other stuffs
# if using COLAB must authenticate first with google drive
from google.colab import drive
drive.mount('drive')

# write the dataframe to CSV and copy to drive/directory
df_out.to_csv('CMCdata.csv', sep='\t', encoding='utf-8')
!cp CMCdata.csv "drive/My Drive/PhDstuffs"