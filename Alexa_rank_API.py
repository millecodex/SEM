#!/usr/bin/env python
# coding: utf-8

# In[90]:


# This script will contact AWS's Alexa API to gather info about cryptocurrency projects based on their URL
# 
# 
#
import pandas as pd 
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from datetime import datetime
import time
url_1 = 'bitcoin.org/'
url_2 = 'ethereum.org/'
url_3 = 'cardano.org/'
url_4 = 'uniswap.org/'

# ************* REQUEST VALUES *************
host = 'awis.api.alexa.com'
endpoint = 'https://' + host
#region = 'us-east-1'
method = 'GET'
service = 'execute-api'
#log = logging.getLogger( "awis" )
content_type = 'application/json'
#local_tz = "America/Los_Angeles"

# Create a date for headers and the credential string
t = datetime.utcnow()
amzdate = t.strftime('%Y%m%dT%H%M%SZ')
datestamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope

# host = 'awis.api.alexa.com' is added automatically to the header 
# by the Python 'requests' library.
headers = {
    'Accept': 'application/json',
    'Content-Type': content_type,
    'X-Amz-Date': amzdate,
    'x-api-key': 'XLuovZkZNi99LcgHf1Zq06AhMd0o8JJy2A7Xo70J'
}

params = (
    ('Action', 'UrlInfo'),
    ('ResponseGroup', 'Rank'),
    ('Url', url_1),
)

url_L = 'https://awis.api.alexa.com/api?Action=UrlInfo&ResponseGroup=Rank&Url='
url_R = 'yahoo.com'

request_url = 'https://awis.api.alexa.com/api'


# In[91]:


#r = requests.get(request_url, headers=headers)
#print(r.text)

try:
    r = session.get(request_url, headers=headers, params=params)
#    j = json.loads(r.text)
except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)


# In[92]:


print('Response code: %d\n' % r.status_code)


# In[93]:


r.text


# In[ ]:


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


# In[ ]:


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


# In[ ]:


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
  'X-CMC_PRO_API_KEY': '5cbb1552-e1d6-4a75-a97b-d1af64d73856',
}
session = Session()
session.headers.update(headers)

try:
  response = session.get(url, params=parameters)
  metadata = json.loads(response.text)
except (ConnectionError, Timeout, TooManyRedirects) as e:
  print(e)


# In[ ]:


# findRepo takes the SourceCode string and strips the domain
# this can be useful for querying GitHub databases
def findRepo(string):
  if string[1:-1]=='':
    return 'none'
  elif string.find('github') > 0:
    return string[19:]
  elif string.find('gitlab') > 0:
    return string[18:]
  else:
    return string[8:]

# extract the host from the SourceCode string
# only really interested in GitHub and GitLab
def findHost(string):
  if string[1:-1]=='':
    return 'none'
  elif string.find('github') > 0:
    return 'github'
  elif string.find('gitlab') > 0:
    return 'gitlab'
  else:
    return 'other'


# In[ ]:


s1='https://github.com/bitcoin/'
s2=''
s3='https://cardanoupdates.com/'
s4='https://github.com/WrappedBTC/bitcoin-token-smart-contracts'
findRepo(s4)


# In[ ]:


# access date::<key>::urls::sourcecode field
# json order is not preserved so build an array containing:
# [ [id, sourcecode], [id,sourcecode],...,[id,sourcecode]]
# where id is CMC unique id
source=[]
for project in metadata['data']:
  id = project
  sc = metadata['data'][id]['urls']['source_code']
  # turn the sc list into a string and trim the ['']
  #print(sc)
  host = findHost(str(sc)[2:-2])
  repo = findRepo(str(sc)[2:-2])
  element = [id,str(sc)[2:-2],host,repo]
  source.append(element)

# create dataframe from this list so it can be merged 
dfsource = pd.DataFrame(data=source,columns=['CMC_id','Source_code','Host','Repo'])


# In[ ]:


df = pd.DataFrame({'CMC_id':cmc_id}) 
# add columns, probably a more elegant way to do this
df['CMC_rank']=cmc_rank
df['name']=name
df['ticker']=ticker

# DF is an INT type and DFSOURCE is a STRING type, cast df as string to merge
# df.astype(str)
df_out=pd.merge(df.astype(str),dfsource, on=['CMC_id'])


# In[ ]:


# write to a CSV for doing other stuffs
# if using COLAB 
must authenticate first with google drive
from google.colab import drive
drive.mount('drive')


# In[ ]:


# write the dataframe to CSV and copy to drive/directory
df_out.to_csv('CMCdata.csv', sep='\t', encoding='utf-8')
get_ipython().system('cp CMCdata.csv "drive/My Drive/PhDstuffs"')


# In[ ]:


df_out.head()


# In[ ]:




