#!/usr/bin/env python3

from urllib.request import urlopen
import base58
import ecdsa
import hashlib
import json
import sys
import time

def check_tx(address):
	txid = []
	cdx = []
	try:
		htmlfile = urlopen("https://mempool.space/api/address/%s" % address, timeout = 20)
	except:
		htmlfile = urlopen("https://mempool.space/api/address/%s" % address, timeout = 20)
	res = json.loads(htmlfile.read())
	funded=res['chain_stats']['funded_txo_sum']
	spent=res['chain_stats']['spent_txo_sum']
	bal=funded-spent
	return bal

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex))

def pvk_to_pubkey(h):
	sk = ecdsa.SigningKey.from_string(h, curve=ecdsa.SECP256k1)
	vk = sk.verifying_key
	return (b'\04' + sk.verifying_key.to_string()).hex()

def pubkey_to_addr(pk):
	if (ord(bytearray.fromhex(pk[-2:])) % 2 == 0):
		public_key_compressed = '02'
	else:
		public_key_compressed = '03'
	public_key_compressed += pk[2:66]
	hex_str = bytearray.fromhex(public_key_compressed)
	sha = hashlib.sha256()
	sha.update(hex_str)
	key_hash = hashlib.new('ripemd160',sha.digest()).hexdigest()
	modified_key_hash = '00' + key_hash
	sha = hashlib.sha256()
	hex_str = bytearray.fromhex(modified_key_hash)
	sha.update(hex_str)
	sha_2 = hashlib.sha256()
	sha_2.update(sha.digest())
	checksum = sha_2.hexdigest()[:8]
	byte_25_address = modified_key_hash + checksum
	return base58.b58encode(bytes(bytearray.fromhex(byte_25_address))).decode('utf-8')

i=2

while i<=0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff:
	i=i*2
	j=i+0x31337
	h=hex(j)[2:]
	while len(h)<64:
		h='0'+h
	print(h,end='\t',flush=True)
	p=pvk_to_wif2(h)
	pubkey=pvk_to_pubkey(bytes.fromhex(h))
	a=pubkey_to_addr(pubkey)
	time.sleep(1)
	b=check_tx(a)
	if b>0:
		print('\apvk: '+p,flush=True)
	print('{0:.8f}'.format(b/100000000)+' BTC',flush=True)
