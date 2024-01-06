#!/usr/bin/env python3

from multiprocessing.pool import Pool
from subprocess import check_output
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import ecdsa
import hashlib
import math
import random
import sys

div=16384
start=0x20000000000000000
end=0x3ffffffffffffffff
rng=0x3ffffffffffffffff-0x20000000000000000
stepout=int(rng/div)
stepin=0x200000000
right='13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so'
print('target: '+right)

def int_to_bytes3(value, length = None): # in: int out: bytearray(b'\x80...
	if not length and value == 0:
		result = [0]
	else:
		result = []
		for i in range(0, length or 1+int(math.log(value, 2**8))):
			result.append(value >> (i * 8) & 0xff)
		result.reverse()
	return bytearray(result)

def pvk_bin_to_addr(pvk):
	signing_key = ecdsa.SigningKey.from_string(pvk, curve = ecdsa.SECP256k1)
	verifying_key = signing_key.get_verifying_key()
	public_key = bytes.fromhex("04") + verifying_key.to_string()

	sha256_1 = hashlib.sha256(public_key)

	ripemd160 = hashlib.new("ripemd160")
	ripemd160.update(sha256_1.digest())

	hashed_public_key = bytes.fromhex("00") + ripemd160.digest()
	checksum_full = hashlib.sha256(hashlib.sha256(hashed_public_key).digest()).digest()
	checksum = checksum_full[:4]
	bin_addr = hashed_public_key + checksum

	return base58.b58encode(bin_addr).decode()

global c
c=0

def go(r):
	global c
	if c%100==0:
		print(f'\r{c:,}'.replace(',',' '),end='     ')
	c=c+1
	by=int_to_bytes3(r,32)
	ad=pvk_bin_to_addr(by)
	#print('\r'+ad,end='')
	if ad==right:
		print('found!')
		print(r)
		print(hex(r))
		print('\a')
		with open('found.txt','w') as f:
			f.write(str(r))
			f.write('\n')
			f.write(hex(r))
			f.write('\n')
			f.flush()
		sys.exit(0)
	return

def n(a,b):
	return list(range(a,b))

s=int(rng/div)
pool = Pool(10)

u=1048576
while True:
	ra=random.randint(start,end-u)
	rb=ra+u
	print(f'\rfrom: {hex(ra)} to: {hex(rb)} range: {hex(u)}={u}')
	#global c
	c=0
	pool.map(go, range(ra,rb), chunksize=32768)

pool.close()
pool.join()
