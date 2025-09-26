#!/usr/bin/env python3

# pip3 install ecpy web3

from Crypto.Hash import keccak
from ecpy.curves import Curve
from multiprocessing import Pool
from tqdm import tqdm
from web3 import Web3
import hashlib
import sys, base58, os

r = [-1000, -100, -3, -2, -1, 0, 1, 2, 3, 100, 1000]

def go(l):
	l=l.decode().rstrip('\n')
	x = int(l, 16)

	for i in r:
		private_key=x+i
		cv = Curve.get_curve('secp256k1')
		try:
			pu_key = private_key * cv.generator # just multiplying the private key by generator point (EC multiplication)
			concat_x_y = pu_key.x.to_bytes(32, byteorder='big') + pu_key.y.to_bytes(32, byteorder='big')
		except:
			return

		k=keccak.new(digest_bits=256)
		k.update(concat_x_y)
		eth_addr = '0x' + k.hexdigest()[-40:]

		cksum=Web3.to_checksum_address(eth_addr)
		with open('output.txt','a') as outfile:
			outfile.write(f'{hex(private_key)[2:].zfill(64)} {cksum}\n')

def main():
	tmp = 0
	cnt = 10000
	th=24
	i=0

	size = os.path.getsize('input.txt')
	infile=open('input.txt','rb')

	if os.path.exists("output.txt"):
		os.remove("output.txt")

	with Pool(processes=th) as p, tqdm(total=size, unit='B', unit_scale=True) as pbar:
		for result in p.imap_unordered(go, infile, chunksize=1000):
			pos=infile.tell()
			r=pos-tmp
			if r>cnt:
				tmp=pos
				pbar.update(r)
				pbar.refresh()

	print('\a', end='', file=sys.stderr)

if __name__ == "__main__":
	main()
