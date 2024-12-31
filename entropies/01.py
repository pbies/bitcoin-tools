#!/usr/bin/env python3

from ecdsa import SigningKey, SECP256k1
from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
import sys, hashlib

hdwallet = HDWallet(symbol=BTC)
order = SECP256k1.order

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def entropy_to_pvk(e):
	entropy_int = int(e, 16)
	if entropy_int >= order or entropy_int < 1:
		return None
	private_key = SigningKey.from_secret_exponent(entropy_int, curve=SECP256k1)
	private_key_bytes = private_key.to_string()
	return private_key_bytes.hex()

def go(i):
	j=str(i).encode()
	k=hashlib.sha256(j).hexdigest()[0:32]
	p=entropy_to_pvk(k)
	if p==None:
		return
	try:
		w=pvk_to_wif2(p)
		hdwallet.from_private_key(p)
	except:
		return
	r=w+'\n'
	r+=hdwallet.wif()+'\n'
	r+=hdwallet.p2pkh_address()+'\n'
	r+=hdwallet.p2sh_address()+'\n'
	r+=hdwallet.p2wpkh_address()+'\n'
	r+=hdwallet.p2wpkh_in_p2sh_address()+'\n'
	r+=hdwallet.p2wsh_address()+'\n'
	r+=hdwallet.p2wsh_in_p2sh_address()+'\n\n'
	outfile.write(r)
	outfile.flush()

def gen():
	for r in range(0, 2**32):
		yield r

outfile = open('output.txt','w')

process_map(go, gen(), max_workers=16, chunksize=1000)

print('\a', end='', file=sys.stderr)
