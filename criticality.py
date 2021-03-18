import pandas as pd

# Read CSV file into DataFrame df
df = pd.read_csv('drive/MyDrive/PhDstuffs/CMCdata_200.csv', index_col=0)

# Show dataframe
#print(df)

df.head()

df2 = pd.read_csv('drive/MyDrive/PhDstuffs/Project_Criticality_all.csv')

# Show dataframe
df2.head()

# add columns to CMC data for criticality
df['criticality']='none'
df.head()

# try searching by 'name' (case-insensitive) to match with CMC data

# loop through CMC data (df)
# for row in df
#     name_sample=df[row][name]
#     if search df2 for row[name_sample]
#         df[criticality] = 'criticality_score'
# 

for row in df.itertuples():
  name=row.name
  for row2 in df2.itertuples():
    if name==row2.name: print('found')

dfs = df.iloc[:7]
df2s= df2.iloc[:50]

"""This results in many named duplicates, for example:
Found: Terra, 0.44098000000000004
Found: Terra, 0.11259000000000001
Found: Terra, 0.11035
Found: Monero, 0.6229899999999999
Found: Cosmos, 0.63302
Found: Cosmos, 0.5687
Found: Cosmos, 0.4926
Found: Cosmos, 0.43818
Found: Cosmos, 0.38327
Found: Cosmos, 0.36705
Found: Cosmos, 0.2116
Found: Solana, 0.67805
Found: IOTA, 0.25358
Found: IOTA, 0.16330999999999998
"""
for row in df.itertuples():
  name = row.name
  for row2 in df2.itertuples():
    if name.casefold() == str(row2.name).casefold():
      criticality=row2.criticality_score
      print("Found: "+name+", "+str(criticality))

num=1
for row in df.itertuples():
  url = str(row.Source_code)
  # trim possible '/' from CMCdata source_code strings (should do this when parsing the cmc data)
  if url[-1]=='/':
    url=url[:-1]
  for row2 in df2.itertuples():
    if url == row2.url:
      criticality=row2.criticality_score
      print(str(num)+" "+url+",\t"+str(criticality))
      num=num+1

# sample output:
"""
1 https://github.com/bitcoin/bitcoin,	0.86864
2 https://github.com/ethereum/go-ethereum,	0.8229700000000001
3 https://github.com/ripple/rippled,	0.63159
4 https://github.com/smartcontractkit/chainlink,	0.6142
5 https://github.com/stellar/stellar-core,	0.59529
6 https://github.com/dogecoin/dogecoin,	0.51976
7 https://github.com/aave/aave-protocol,	0.25848000000000004
8 https://github.com/monero-project/monero,	0.6229899999999999
9 https://github.com/cosmos/cosmos-sdk,	0.7429399999999999
10 https://github.com/solana-labs/solana,	0.67805
11 https://github.com/iotaledger/iota.js,	0.41771
12 https://github.com/EOSIO/eos,	0.7085100000000001
13 https://github.com/bitcoin-sv/bitcoin-sv,	0.47458999999999996
14 https://github.com/tronprotocol/java-tron,	0.62134
15 https://github.com/ava-labs/avalanchego,	0.50151
16 https://github.com/sushiswap/sushiswap,	0.30666
17 https://github.com/compound-finance/compound-protocol,	0.33549
18 https://github.com/Zilliqa/Zilliqa,	0.59758
19 https://github.com/zcash/zcash,	0.75193
20 https://github.com/RavenProject/Ravencoin,	0.55743
21 https://github.com/qtumproject/qtum,	0.5528
22 https://github.com/BTCGPU/BTCGPU,	0.42257
23 https://github.com/golemfactory/golem,	0.43501999999999996
24 https://github.com/ArweaveTeam/arweave,	0.43885
25 https://github.com/OrchidTechnologies/orchid,	0.47928000000000004
26 https://github.com/storj/storj,	0.56045
27 https://github.com/vechain/thor,	0.40387
28 https://github.com/steemit/steem,	0.47662
"""
