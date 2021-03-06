# This script will contact AWS's Alexa API to gather info about cryptocurrency projects based on their URL
# 
# command line access via:
#  !curl -H "x-api-key: XLuov...7Xo70J" "https://awis.api.alexa.com/api?Action=UrlInfo&ResponseGroup=Rank&Url=yahoo.com"
#
# first 1000 calls are free
# 1k to 100K are rounded up are $0.036 per unit (each unit is 10 calls)
# see: https://aws.amazon.com/marketplace/pp/B07Q71HJ3H?ref_=srh_res_product_title
# 
import pandas as pd 
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import xmltodict
from datetime import datetime
import sys,time

# ************* REQUEST VALUES *************
host = 'awis.api.alexa.com'
endpoint = 'https://' + host
#region = 'us-east-1'
method = 'GET'
service = 'execute-api'
#log = logging.getLogger( "awis" )
content_type = 'application/xml'
#local_tz = "America/Los_Angeles"

# Create a date for headers and the credential string
t = datetime.utcnow()
amzdate = t.strftime('%Y%m%dT%H%M%SZ')
datestamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope

# host = 'awis.api.alexa.com' is added automatically to the header 
# by the Python 'requests' library.
# Alexa awis only provides XML
headers = {
    'Accept': 'application/xml',
    'Content-Type': content_type,
    'X-Amz-Date': amzdate,
    'x-api-key': 'xxx'
}

request_url = 'https://awis.api.alexa.com/api'

# Read in '200_websites.csv'
#
# may want to double-check some of the urls for 
# top-level sites (no sub branches); also
# could assess primary and secondary and keep highest ranking (future work)
#
df = pd.read_csv('200_websites.csv', index_col=0)


# getRank takes a dataframe with a column: 'web_primary' and queries awis 
# for rank info
# can also query for traffic info via Action=TrafficHistory
#                & incoming links via Action=SitesLinkingIn
# @return a new column at df.Alexa_rank[rank]
#
def getRank(df):
    num = 0
    for row in df.itertuples():
        # sites that don't respond could be dropped 
        # for restart so Alexa_rank doesn't get overwritten
        # and to save api calls
        #if 'alexa_rank' in df.columns:
        #    if row.alexa_rank > 0:
        #        continue
        #    continue
            
        url = row.web_primary
        params = (
            ('Action', 'UrlInfo'),
            ('ResponseGroup', 'Rank'),
            ('Url', url),
        )
        
        session = Session()
        session.headers.update(headers)
        
        try:
            response = session.get(request_url, headers = headers, params = params)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
            continue
        #print('Response code: %d\n' % response.status_code)
        
        # format response
        my_dict = xmltodict.parse(response.text)
        resp_json = json.dumps(my_dict, indent = 4)
        json_data = json.loads(resp_json)
        
        # get alexa ranking
        rank = json_data['Awis']['Results']['Result']['Alexa']['TrafficData']['Rank']
        
        # update datafram
        df.at[row.Index, 'alexa_rank'] = rank
        num += 1
        sys.stdout.write(".")
        sys.stdout.flush()
    result = str(num)+' Alexa rankings updated'
    return result

# main call
getRank(df)               
        
# write out Alexa rankings
df.to_csv('200_alexa.csv', encoding='utf-8')
    
# update MERGED sheet with new data
# 'CMC_id' is the key
df_temp = pd.read_csv('200_merged.csv', index_col=0)
# the columns ['web_primary', 'web_secondary'] may have been manually updated, so drop them
df_temp.drop(['web_primary', 'web_secondary'], axis = 1, inplace = True)
dfm = pd.merge(df_temp, df, on=['CMC_id'], how = 'outer')

# write out merged data
dfm.to_csv('200_merged.csv', encoding='utf-8', index=0)