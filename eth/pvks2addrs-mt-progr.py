#!/usr/bin/env python3

from Crypto.Hash import keccak
from ecpy.curves import Curve
from tqdm import tqdm
import hashlib
from web3 import Web3
from tqdm.contrib.concurrent import process_map

workers=8

i=open('input.txt','r')
o=open('output.txt','w')

cnt=sum(1 for line in open("input.txt", 'r'))

pbar=tqdm(total=cnt)

t=0

def go(l):
	l=l.strip()
	private_key = int(l,16)

	cv     = Curve.get_curve('secp256k1')
	pu_key = private_key * cv.generator # just multiplying the private key by generator point (EC multiplication)

	concat_x_y = pu_key.x.to_bytes(32, byteorder='big') + pu_key.y.to_bytes(32, byteorder='big')
	k=keccak.new(digest_bits=256)
	k.update(concat_x_y)
	eth_addr = '0x' + k.hexdigest()[-40:]

	cksum=Web3.to_checksum_address(eth_addr)
	o.write(l+' : '+cksum+'\n')
	o.flush()
	global t
	t=t+1
	if t%1000==0:
		pbar.update(1000)

process_map(go, i, max_workers=workers, chunksize=200)

i.close()
o.close()
pbar.close()

import sys
print('\a',end='',file=sys.stderr)
