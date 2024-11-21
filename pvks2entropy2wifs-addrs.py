#!/usr/bin/env python3

from ecdsa import SigningKey, SECP256k1
from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58, re
import os, sys, hashlib

hdwallet = HDWallet(symbol=BTC)
order = SECP256k1.order

def pvk_to_wif(key_bytes):
	return base58.b58encode_check(b'\x80' + key_bytes)

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def entropy_to_pvk(e):
	entropy_int = int(e, 16)
	if entropy_int >= order or entropy_int < 1:
		return None
	private_key = SigningKey.from_secret_exponent(entropy_int, curve=SECP256k1)
	private_key_bytes = private_key.to_string()
	return private_key_bytes.hex()

def find_all_matches(pattern, string):
	pat = re.compile(pattern)
	pos = 0
	out = []
	while (match := pat.search(string, pos)) is not None:
		pos = match.start() + 1
		out.append(match[0])
	return out

def go(k):
	l=find_all_matches('[0-9a-fA-F]{32}', k)
	for m in l:
		p=entropy_to_pvk(m)
		if p==None:
			continue
		w=pvk_to_wif2(p)
		r=w+'\n'
		hdwallet.from_private_key(p)
		r+=hdwallet.wif()+'\n'
		r+=hdwallet.p2pkh_address()+'\n'
		r+=hdwallet.p2sh_address()+'\n'
		r+=hdwallet.p2wpkh_address()+'\n'
		r+=hdwallet.p2wpkh_in_p2sh_address()+'\n'
		r+=hdwallet.p2wsh_address()+'\n'
		r+=hdwallet.p2wsh_in_p2sh_address()+'\n\n'
		outfile.write(r)
		outfile.flush()

print('Reading...')
lines = open('input.txt','r').read().splitlines()
outfile = open('output.txt','w')

print('Writing...')
process_map(go, lines, max_workers=24, chunksize=10000)

print('\a', end='', file=sys.stderr)
