#!/usr/bin/env python3

from Crypto.Hash import keccak
from ecpy.curves import Curve
from tqdm import tqdm
import hashlib

cnt=sum(1 for line in open("input.txt", 'r'))

i=open("input.txt","r")
o=open("output.txt","w")

for l in tqdm(i, total=cnt):
	private_key = int(l.strip(),16)

	cv     = Curve.get_curve('secp256k1')
	pu_key = private_key * cv.generator # just multiplying the private key by generator point (EC multiplication)

	concat_x_y = pu_key.x.to_bytes(32, byteorder='big') + pu_key.y.to_bytes(32, byteorder='big')
	k=keccak.new(digest_bits=256)
	k.update(concat_x_y)
	eth_addr = '0x' + k.hexdigest()[-40:]

	o.write('pvk: '+hex(private_key)+' ')
	o.write('addr: '+eth_addr+'\n')
