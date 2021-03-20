import pandas as pd
import time
import math

# Read CSV file into DataFrame df
df = pd.read_csv('drive/MyDrive/PhDstuffs/CMCdata_200.csv', index_col=0)

# Show dataframe
#print(df)

df2 = pd.read_csv('drive/MyDrive/PhDstuffs/Project_Criticality_all.csv')

# Show dataframe
#df2.head()

# add columns to CMC data for criticality
#df['criticality']='none'
#df.head()

# subset dataframes for testing
dfs = df.iloc[:10]
df2s= df2.iloc[:50]

# searching by project name to pull criticality
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

# search by url ensures unique results, however many are missed
# manual dataset updating required for the url field
start = time.process_time()
# about 41s to process top cmc top 100 via COLAB
num=1
for row in df.itertuples():
  # only search for strings; floats (NaN) are skipped
  if isinstance(row.Source_code, str):
    url = str(row.Source_code)
    # trim possible '/' from CMCdata source_code strings (should do this when parsing the cmc data)
    if url[-1]=='/':
      url=url[:-1]
    # loop through df2 (criticality) looking for source code url
    for row2 in df2.itertuples():
      if url == row2.url:
        criticality=row2.criticality_score
        print(str(num)+" "+url+",\t"+str(criticality))
        num+=1
        break
end = time.process_time()
print("time elapsed = ", end - start)

# 49 in cmc top 100 found:
"""
1 https://github.com/bitcoin/bitcoin,	      0.86864
2 https://github.com/ethereum/go-ethereum,	0.8229700000000001
3 https://github.com/input-output-hk/cardano-node,	0.6350399999999999
4 https://github.com/paritytech/polkadot,	  0.6197199999999999
5 https://github.com/ripple/rippled,	      0.63159
6 https://github.com/Uniswap/uniswap-v2-core,	0.19942000000000001
7 https://github.com/smartcontractkit/chainlink,	0.6142
8 https://github.com/stellar/stellar-core,	0.59529
9 https://github.com/dogecoin/dogecoin,	    0.51976
10 https://github.com/aave/aave-protocol,	  0.25848000000000004
11 https://github.com/vechain/thor,	        0.40387
12 https://github.com/monero-project/monero,	0.6229899999999999
13 https://github.com/cosmos/cosmos-sdk,	  0.7429399999999999
14 https://github.com/solana-labs/solana,	  0.67805
15 https://github.com/iotaledger/iota.js,	  0.41771
16 https://github.com/EOSIO/eos,	          0.7085100000000001
17 https://github.com/bitcoin-sv/bitcoin-sv,	0.47458999999999996
18 https://github.com/tronprotocol/java-tron,	0.62134
19 https://github.com/ava-labs/avalanchego,	0.50151
20 https://github.com/sushiswap/sushiswap,	0.30666
21 https://github.com/neo-project/neo,	    0.6212
22 https://github.com/filecoin-project/lotus,	0.66433
23 https://github.com/algorand/go-algorand,	0.5318
24 https://github.com/makerdao/dss,	        0.45585
25 https://github.com/ElrondNetwork/elrond-go,	0.56316
26 https://github.com/Synthetixio/synthetix,	0.57295
27 https://github.com/graphprotocol/graph-node,	0.55579
28 https://github.com/decred/dcrd,	        0.59037
29 https://github.com/makerdao/market-maker-keeper,	0.32309
30 https://github.com/compound-finance/compound-protocol,	0.33549
31 https://github.com/Zilliqa/Zilliqa,	    0.59758
32 https://github.com/zcash/zcash,	        0.75193
33 https://github.com/RavenProject/Ravencoin,	0.55743
34 https://github.com/bancorprotocol/contracts-solidity,	0.5311
35 https://github.com/wavesplatform/Waves,	0.61635
36 https://github.com/0xProject/0x-monorepo,	0.5889800000000001
37 https://github.com/blockstack/stacks-blockchain,	0.65277
38 https://github.com/ontio/ontology,	      0.44072
39 https://github.com/iost-official/go-iost,	0.4885
40 https://github.com/nanocurrency/nano-node,	0.54171
41 https://github.com/qtumproject/qtum,	    0.5528
42 https://github.com/harmony-one/harmony,	0.5965
43 https://github.com/BTCGPU/BTCGPU,	      0.42257
44 https://github.com/golemfactory/golem,	  0.43501999999999996
45 https://github.com/ArweaveTeam/arweave,	0.43885
46 https://github.com/OrchidTechnologies/orchid,	0.47928000000000004
47 https://github.com/storj/storj,	        0.56045
48 https://github.com/vechain/thor,	        0.40387
49 https://github.com/steemit/steem,	      0.47662
"""


# search by using pandas column search methods
# function from stackexchange
# see: https://stackoverflow.com/questions/26640129/search-for-string-in-all-pandas-dataframe-columns-and-filter
#
def search(regex: str, df, case=False):
    """Search all the text columns of `df`, return rows with any matches."""
    textlikes = df.select_dtypes(include=[object, "string"])
    return df[
        textlikes.apply(
            lambda column: column.str.contains(regex, regex=True, case=case, na=False)
        ).any(axis=1)
    ]
out=search("https://github.com/rust-lang/rust",df2)

