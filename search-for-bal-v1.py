#!/usr/bin/env python3

from random import randrange
from subprocess import check_output
from tqdm import tqdm
import base58
import ecdsa
import hashlib
import os
import sys

a=open("pub.txt","r")
b=a.readlines()
c = [x.rstrip('\n') for x in b]

for i in range(200000):
	Private_key=os.urandom(32)

	signing_key = ecdsa.SigningKey.from_string(Private_key, curve = ecdsa.SECP256k1)
	verifying_key = signing_key.get_verifying_key()
	public_key = bytes.fromhex("04") + verifying_key.to_string()

	sha256_1 = hashlib.sha256(public_key)

	ripemd160 = hashlib.new("ripemd160")
	ripemd160.update(sha256_1.digest())

	hashed_public_key = bytes.fromhex("00") + ripemd160.digest()
	checksum_full = hashlib.sha256(hashlib.sha256(hashed_public_key).digest()).digest()
	checksum = checksum_full[:4]
	bin_addr = hashed_public_key + checksum

	result_address = base58.b58encode(bin_addr).decode('utf-8')
	if result_address in c:
		print(Private_key.decode('utf-8')+":"+result_address+" found")
