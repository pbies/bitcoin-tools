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

url = 'https://mainnet.infura.io/v3/YOUR_API_KEY'
w3 = Web3(Web3.HTTPProvider(url))

headers = {'content-type': 'application/json'}

def go(l):
	private_key = int(l,16)

	cv     = Curve.get_curve('secp256k1')
	pu_key = private_key * cv.generator # just multiplying the private key by generator point (EC multiplication)

	concat_x_y = pu_key.x.to_bytes(32, byteorder='big') + pu_key.y.to_bytes(32, byteorder='big')
	k=keccak.new(digest_bits=256)
	k.update(concat_x_y)
	eth_addr = '0x' + k.hexdigest()[-40:]

	cksum=Web3.to_checksum_address(eth_addr)
	payload = {
		'jsonrpc': '2.0',
		'method': 'eth_getBalance',
		'params': [cksum,'latest'],
		'id': 1
	}
	response = requests.post(url, data=json.dumps(payload), headers=headers).json()
	try:
		bal=int(response['result'],16)
		b='{0:.18f}'.format(bal/1e18)
		o.write(l+' '+cksum+' '+b+'\n')
	except:
		pass
	o.flush()

print('Reading...')
i=open('input.txt','r').read().splitlines()

print('Writing...')
o=open('output.txt','w')
process_map(go, i, max_workers=workers, chunksize=100)
#for x in tqdm(i):
#	go(x)

o.close()

print('Done!\a', file=sys.stderr)
