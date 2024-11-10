#!/usr/bin/env python3

from web3 import Web3
from tqdm.contrib.concurrent import process_map

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/YBYyZuWJpHTkq_ufppjI1HHoUB69NCi2"
w3 = Web3(Web3.HTTPProvider(alchemy_url))

# print(w3.is_connected())

outfile = open("output.txt","a")

cnt=sum(1 for line in open("hits.txt", 'r'))

def worker(key):
    bal=w3.eth.get_balance(key,"latest")
    if bal>0:
        print("Found one!")
    outfile.write(key+" "+str(bal)+"\n")
    outfile.flush()

f=open("hits.txt","r")
lines=f.readlines()
lines = [x.strip() for x in lines]
lines = [w3.to_checksum_address(x) for x in lines]

process_map(worker, lines, max_workers=4, chunksize=3000)
