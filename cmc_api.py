from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

# listing of top 200 (per 1 credit) by market cap
# default sort is by market cap
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

# access CMC_ID field in JSON to use for metadata
cmc_id=[]
for project in data_listing['data']:
  cmc_id.append(project['id'])

# access NAME field in JSON to build dataframe
name=[]
for project in data_listing['data']:
  name.append(project['name'])

# access SYMBOL (ticker) field in JSON to build dataframe
ticker=[]
for project in data_listing['data']:
  ticker.append(project['symbol'])

# access RANK field in JSON to build dataframe
cmc_rank=[]
for project in data_listing['data']:
  cmc_rank.append(project['cmc_rank'])

# trim the lists for testing
testID=cmc_id[0:15]
testName=name[0:15]
testTicker=ticker[0:15]
testRank=cmc_rank[0:15]

#IDString=''
#for id in cmc_id:
#    IDString = IDString + str(id) +','
#IDString = IDString[:-1]
testIDString=''
for id in testID:
    testIDString = testIDString + str(id) +','
testIDString = testIDString[:-1]
#print(testIDString)

# listing of metadata
url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'
parameters = {
  'id':testIDString,
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
  element = [id,sc]
  source.append(element)

import pandas as pd 
 
# Creates DataFrame. {'col':L}
df = pd.DataFrame({'CMC_id':testID})

#df['source code']=1
df['name']=testName
df['ticker']=testTicker
df['CMC_rank']=testRank

df2 = pd.DataFrame(data=source,columns=['CMC_id','Source_code'])

#df is in int type and df2 is a string type, cast df as string to merge
#df.astype(str)
df3=pd.merge(df.astype(str),df2, on=['CMC_id'])
df3

