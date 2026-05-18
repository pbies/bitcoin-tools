#!/usr/bin/env python3

from Crypto.Hash import keccak
from ecpy.curves import Curve
from tqdm import tqdm
import hashlib
from web3 import Web3
from tqdm.contrib.concurrent import process_map

workers=4

alchemy_url = 'https://eth-mainnet.g.alchemy.com/v2/'
w3 = Web3(Web3.HTTPProvider(alchemy_url))
w3.eth.account.enable_unaudited_hdwallet_features()

i=open('input.txt','r')
o=open('output.txt','w')

def go(l):
	private_key = int(l,16)

	cv     = Curve.get_curve('secp256k1')
	pu_key = private_key * cv.generator # just multiplying the private key by generator point (EC multiplication)

	concat_x_y = pu_key.x.to_bytes(32, byteorder='big') + pu_key.y.to_bytes(32, byteorder='big')
	k=keccak.new(digest_bits=256)
	k.update(concat_x_y)
	eth_addr = '0x' + k.hexdigest()[-40:]

	cksum=Web3.to_checksum_address(eth_addr)
	bal=w3.eth.get_balance(cksum,'latest')

	o.write(l+' : '+cksum+' : '+str(bal)+'\n')
	o.flush()

def main():
	print('Reading...', flush=True)
	lines=i.readlines()
	lines = [x.strip() for x in lines]

	print('Writing...', flush=True)
	process_map(go, lines, max_workers=workers, chunksize=1000)

	i.close()
	o.close()

	import sys
	print('All OK\a',file=sys.stderr)

if __name__ == '__main__':
	main()
