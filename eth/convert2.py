#!/usr/bin/env python3

# https://docs.alchemy.com/reference/alchemy-gettokenbalances

import requests
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from pprint import pprint
import json
from web3.auto import w3
from web3 import Web3

url = 'https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY'

cnt = sum(1 for line in open("addrs-pvks-rich.txt", 'r'))

input_file=open('addrs-pvks-rich.txt','r')
o=open('output.txt','a')

#w3 = Web3(Web3.HTTPProvider(url))
#w3.eth.account.enable_unaudited_hdwallet_features()

def go(a):
	line=a.strip()

	addr=line[:42]
	pvk=line[43:]

	payload = {
		"id": 1,
		"jsonrpc": "2.0",
		"method": "alchemy_getTokenBalances",
		"params": [addr]
	}
	headers = {
		"accept": "application/json",
		"content-type": "application/json"
	}

	j1 = requests.post(url, json=payload, headers=headers).text
	j2=json.loads(j1)['result']
	addr2=j2['address']
	for i in j2['tokenBalances']:
		ca=i['contractAddress']
		tb=str(int(i['tokenBalance'][2:],16))
		if tb!='0':
			o.write('address:'+addr+' pvk:'+pvk+' contractaddress:'+ca+' balance:'+tb+'\n')

	o.flush()

process_map(go, input_file, max_workers=10, chunksize=10000)

o.close()

import sys
print('\a',end='',file=sys.stderr)
