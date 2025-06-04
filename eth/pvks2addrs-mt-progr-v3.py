#!/usr/bin/env python3

from Crypto.Hash import keccak
from ecpy.curves import Curve
from tqdm import tqdm
import hashlib
from web3 import Web3
from tqdm.contrib.concurrent import process_map

workers=16

def go(l):
	private_key = int(l, 16)

	cv     = Curve.get_curve('secp256k1')
	pu_key = private_key * cv.generator # just multiplying the private key by generator point (EC multiplication)

	concat_x_y = pu_key.x.to_bytes(32, byteorder='big') + pu_key.y.to_bytes(32, byteorder='big')
	k=keccak.new(digest_bits=256)
	k.update(concat_x_y)
	eth_addr = '0x' + k.hexdigest()[-40:]

	cksum=Web3.to_checksum_address(eth_addr)
	o.write(l+' : '+cksum+'\n')
	o.flush()

print('Reading...', flush=True)
i=open('input.txt','r').read().splitlines()

print('Writing...', flush=True)
o=open('output.txt','w')
process_map(go, i, max_workers=workers, chunksize=10000)

o.close()

import sys
print('All OK\a', file=sys.stderr)
