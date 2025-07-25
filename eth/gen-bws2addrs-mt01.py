#!/usr/bin/env python3

from Crypto.Hash import keccak
from ecpy.curves import Curve
from tqdm import tqdm
import hashlib
from web3 import Web3
from multiprocessing import Pool
from tqdm import tqdm
import sys, base58, os

tmp = 0
cnt = 1000
th=28
c=0

print('Generate...')
infile=[]
for i in list(range(0,10**8)):
	infile.append(str(i))

outfile = open('output.txt','w')

def go(l):
	#l=l.rstrip(b'\n')
	x=hashlib.sha256(l.encode()).hexdigest()
	private_key = int(x, 16)

	cv     = Curve.get_curve('secp256k1')
	try:
		pu_key = private_key * cv.generator # just multiplying the private key by generator point (EC multiplication)
		concat_x_y = pu_key.x.to_bytes(32, byteorder='big') + pu_key.y.to_bytes(32, byteorder='big')
	except:
		return

	k=keccak.new(digest_bits=256)
	k.update(concat_x_y)
	eth_addr = '0x' + k.hexdigest()[-40:]

	#cksum=Web3.to_checksum_address(eth_addr)
	outfile.write(f'{eth_addr} {x} {l}\n')
	outfile.flush()

print('Write...')
with Pool(processes=th) as p, tqdm(total=len(infile)) as pbar:
	for result in p.imap_unordered(go, infile, chunksize=1000):
		c=c+1
		if c%cnt==0:
			pbar.update(cnt)
			pbar.refresh()

outfile.close()

print('\a', end='', file=sys.stderr)
