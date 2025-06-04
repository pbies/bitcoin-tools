#!/usr/bin/env python3

from Crypto.Hash import keccak
from ecpy.curves import Curve
from multiprocessing import Pool
from tqdm import tqdm
from web3 import Web3
import json
import requests
import sys

th=4

url = 'https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY'
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
	try:
		response = requests.post(url, data=json.dumps(payload), headers=headers).json()
	except:
		e=open('errors.txt','a')
		e.write(f'{l} {cksum}\n')
		e.flush()
		e.close()
		return
	try:
		bal=int(response['result'],16)
		b='{0:.18f}'.format(bal/1e18)
		o.write(f'{b} {cksum} {l}\n')
	except:
		pass
	o.flush()

print('Reading...', flush=True)
i=open('input.txt','r').read().splitlines()

print('Writing...', flush=True)
o=open('output.txt','w')

if __name__=='__main__':
	max_=len(i)
	c=0
	with Pool(processes=th) as p, tqdm(total=max_) as pbar:
		for result in p.imap_unordered(go, i, chunksize=1000):
			if c%100==0:
				pbar.update(100)
				pbar.refresh()
			c=c+1

	o.close()

	print('Done!\a', file=sys.stderr)
