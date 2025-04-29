#!/usr/bin/env python3

from multiprocessing import Pool
from tqdm import tqdm
import base58
import datetime
import ecdsa
import hashlib
import os
import random

def private_key_to_address(private_key_bytes):
	sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
	vk = sk.get_verifying_key()
	pub_key = b'\x04' + vk.to_string()

	sha256_1 = hashlib.sha256(pub_key).digest()
	ripemd160 = hashlib.new('ripemd160')
	ripemd160.update(sha256_1)
	hashed_pubkey = ripemd160.digest()

	mainnet_pubkey = b'\x00' + hashed_pubkey
	checksum = hashlib.sha256(hashlib.sha256(mainnet_pubkey).digest()).digest()[:4]
	binary_address = mainnet_pubkey + checksum
	address = base58.b58encode(binary_address)
	return address.decode()

addr='1ELCrM2FMXePtsGLRbcqAdhj61EUGmUtK9'
p1=0x414ebfe886361d9e9cb2f5d46bfe1c3f1523fe80830600000000000000000000
p2=0x414ebfe886361d9e9cb2f5d46bfe1c3f1523fe80830700000000000000000000
r=range(p1,p2)
l=p2-p1
# pubkey = 03f31ec8aae7bda56cd61a5e464a0ed84d8813db3cfa3dc91261d6701893ba70ae
# ./keyhunt -m bsgs -k 2048 -t 28 -s 5 -S -R -q -f pubkey-other.txt -r 414ebfe886361d9e9cb2f5d46bfe1c3f1523fe80830600000000000000000000:414ebfe886361d9e9cb2f5d46bfe1c3f1523fe80830700000000000000000000

def log(message):
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	formatted = f"{timestamp} {message}"
	print(formatted, flush=True, end='')
	with open('log.txt', 'a') as logfile:
		logfile.write(formatted)
		logfile.flush()

def int_to_bytes4(number, length): # in: int, int
	return number.to_bytes(length,'big')

th=30
CHUNK_SIZE=1024
PROGRESS_COUNT = 1024
size=1048576

def go(p):
	a=private_key_to_address(int_to_bytes4(p,32))
	if a==addr:
		log(f'\a\npvk: {hex(p)} addr: {a}\n')

os.system('cls||clear')

while True:
	z=random.randint(p1,p2)
	y=range(z, z+size+1)
	log(f'range: {hex(z)[2:]}:{hex(z+size)[2:]}\n')
	with Pool(processes=th) as pool:
		for result in pool.imap_unordered(go, y, chunksize=CHUNK_SIZE):
			pass
