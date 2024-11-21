#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
import base58
import hashlib
import sys

hdwallet = HDWallet(symbol=BTC)

def sha(k):
	sha = hashlib.sha256()
	sha.update(k)
	return sha.hexdigest()

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

outfile = open('output.txt','w')

def go(i):
	a=hex(i)[2:]
	b=sha(a.encode())
	c=b[0:32]
	d=hdwallet.from_entropy(c)
	e=hdwallet.private_key()
	f=pvk_to_wif2(e)

	r=f+'\n'
	r+=hdwallet.wif()+'\n'
	r+=hdwallet.p2pkh_address()+'\n'
	r+=hdwallet.p2sh_address()+'\n'
	r+=hdwallet.p2wpkh_address()+'\n'
	r+=hdwallet.p2wpkh_in_p2sh_address()+'\n'
	r+=hdwallet.p2wsh_address()+'\n'
	r+=hdwallet.p2wsh_in_p2sh_address()+'\n\n'

	outfile.write(r)
	outfile.flush()

process_map(go, range(0, 2**16+1), max_workers=24, chunksize=10000)

print('\a', end='', file=sys.stderr)
