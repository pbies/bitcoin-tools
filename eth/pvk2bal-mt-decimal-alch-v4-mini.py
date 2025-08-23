#!/usr/bin/env python3

from Crypto.Hash import keccak
from ecpy.curves import Curve
from eth_keys import keys
from eth_utils import to_checksum_address
from subprocess import check_output
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from web3 import Web3
import base58
import hashlib
import json
import os
import requests
import sys

workers=4

url = 'https://eth-mainnet.g.alchemy.com/v2/'
w3 = Web3(Web3.HTTPProvider(url))

headers = {'content-type': 'application/json'}

def go(l):
	cksum=l
	payload = {
		'jsonrpc': '2.0',
		'method': 'eth_getBalance',
		'params': [cksum,'latest'],
		'id': 1
	}
	try:
		response = requests.post(url, data=json.dumps(payload), headers=headers).json()
	except:
		e=open('errors.txt','a')
		e.write(l+' '+cksum+'\n')
		e.flush()
		e.close()
		return
	try:
		bal=int(response['result'],16)
		b='{0:.18f}'.format(bal/1e18)
		o.write(cksum+' '+b+'\n')
	except:
		pass
	o.flush()

print('Reading...', flush=True)
i=open('input.txt','r').read().splitlines()

print('Writing...', flush=True)
o=open('output.txt','w')
process_map(go, i, max_workers=workers, chunksize=100)
#for x in tqdm(i):
#	go(x)

o.close()

print('Done!\a', file=sys.stderr)
