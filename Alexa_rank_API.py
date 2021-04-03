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
    'x-api-key': 'XXX'
}

params = (
    ('Action', 'UrlInfo'),
    ('ResponseGroup', 'Rank'),
    ('Url', url_1),
)

url_L = 'https://awis.api.alexa.com/api?Action=UrlInfo&ResponseGroup=Rank&Url='
url_R = 'yahoo.com'

request_url = 'https://awis.api.alexa.com/api'


try:
    r = session.get(request_url, headers=headers, params=params)
#    j = json.loads(r.text)
except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)


print('Response code: %d\n' % r.status_code)
r.text