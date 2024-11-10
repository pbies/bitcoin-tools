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

url = "https://mainnet.infura.io/v3/YOUR_API_KEY"
w3 = Web3(Web3.HTTPProvider(url))

headers = {'content-type': 'application/json'}

lines = open('input.txt','r').read().splitlines()
outfile = open("result.txt","w")

def go(x):
	private_key = keys.PrivateKey(bytes.fromhex(x))
	public_key = private_key.public_key
	eth_address = public_key.to_address()
	checksum_address = to_checksum_address(eth_address)
	payload = {
		"jsonrpc": "2.0",
		"method": "eth_getBalance",
		"params": [checksum_address,'latest'],
		"id": 1
	}
	response = requests.post(url, data=json.dumps(payload), headers=headers).json()
	outfile.write(x+' '+checksum_address+' '+str(int(response['result'],16))+"\n")
	outfile.flush()

process_map(go, lines, max_workers=4, chunksize=1000)

#for i in tqdm(lines):
#	go(i)
