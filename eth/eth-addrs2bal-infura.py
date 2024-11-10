#!/usr/bin/env python3

from Crypto.Hash import keccak
from ecpy.curves import Curve
from subprocess import check_output
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from web3 import Web3
import base58
import hashlib
import os
import requests
import json
from eth_keys import keys
from eth_utils import to_checksum_address

url = 'https://mainnet.infura.io/v3/YOUR_API_KEY'
w3 = Web3(Web3.HTTPProvider(url))

headers = {'content-type': 'application/json'}

lines = open('input.txt','r').read().splitlines()
outfile = open('result.txt','a')

def go(x):
	checksum_address = x
	payload = {
		'jsonrpc': '2.0',
		'method': 'eth_getBalance',
		'params': [checksum_address,'latest'],
		'id': 1
	}
	response = requests.post(url, data=json.dumps(payload), headers=headers).json()
	try:
		outfile.write(x+' '+str(int(response['result'],16))+'\n')
	except:
		return
	outfile.flush()

process_map(go, lines, max_workers=4, chunksize=100)

#for i in tqdm(lines):
#	go(i)
import sys
print('Done!\a', file=sys.stderr)
