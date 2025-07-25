#!/usr/bin/env python3

from Crypto.Hash import keccak
from ecpy.curves import Curve
from multiprocessing import Pool
from tqdm import tqdm
from web3 import Web3
import hashlib
import sys, base58, os, time

tmp = 0
cnt = 1000
th=28
c=0

print('Generate...')
infile=[]
start_time=time.time()
infile = [str(line) for line in range(0,10**8)]
stop_time=time.time()
print(f'Generate took: {stop_time-start_time:.3f} seconds')

if os.path.exists("output.txt"):
	os.remove("output.txt")

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
	with open('output.txt','a') as outfile:
		outfile.write(f'{eth_addr} {x} {l}\n')

print('Write...')
with Pool(processes=th) as p, tqdm(total=len(infile)) as pbar:
	for result in p.imap_unordered(go, infile, chunksize=th*4):
		c=c+1
		if c%cnt==0:
			pbar.update(cnt)
			pbar.refresh()

outfile.close()

print('\a', end='', file=sys.stderr)
