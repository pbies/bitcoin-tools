#!/usr/bin/env python3

from web3 import Web3
from tqdm.contrib.concurrent import process_map
from ecpy.curves import Curve
from Crypto.Hash import keccak
from tqdm import tqdm
import os

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/gafwMFYujIM8fQ3gkJsfUoVGp6AyH6EC"
w3 = Web3(Web3.HTTPProvider(alchemy_url))

outfile = open("eth.txt","a")

cnt=20000000

def bytes_to_int(bytes):
	return int.from_bytes(bytes,"big")

for i in tqdm(range(1,cnt+1), total=cnt):
	private_key=i
	cv	 = Curve.get_curve('secp256k1')
	pu_key = private_key * cv.generator # just multiplying the private key by generator point (EC multiplication)
	concat_x_y = pu_key.x.to_bytes(32, byteorder='big') + pu_key.y.to_bytes(32, byteorder='big')
	k=keccak.new(digest_bits=256)
	eth_addr = '0x' + k.update(concat_x_y).digest()[-20:].hex()
	bal=w3.eth.get_balance(w3.to_checksum_address(eth_addr),"latest")
	if bal>0:
		print("Found one! Private key:",i,"Balance:{:.18f}".format(bal/10e18),"ETH")
	if bal>=15000000000000000:
		print("\a")
	outfile.write(str(private_key)+" "+eth_addr+" "+str(bal)+"\n")
	outfile.flush()
