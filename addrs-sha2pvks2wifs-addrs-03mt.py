#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
from tqdm import tqdm
import sys, hashlib, base58

hdwallet = HDWallet(symbol=BTC)

print('Reading...', flush=True)
i=open("input.txt","rb").read().splitlines()

o = open("output.txt","w")

def shahex(x):
	return hashlib.sha256(x).hexdigest()

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(x):
	try:
		d=base58.b58decode_check(x)
	except:
		return
	s=shahex(d)
	hdwallet.from_private_key(private_key=s)
	wif = pvk_to_wif2(s)

	output_lines=wif + '\n'
	output_lines+=hdwallet.wif() + '\n'
	output_lines+=hdwallet.p2pkh_address() + '\n'
	output_lines+=hdwallet.p2sh_address() + '\n'
	output_lines+=hdwallet.p2wpkh_address() + '\n'
	output_lines+=hdwallet.p2wpkh_in_p2sh_address() + '\n'
	output_lines+=hdwallet.p2wsh_address() + '\n'
	output_lines+=hdwallet.p2wsh_in_p2sh_address() + '\n\n'

	o.write(output_lines)
	o.flush()

print('Writing...', flush=True)

process_map(go, i, max_workers=16, chunksize=1000)

print('\a', end='', file=sys.stderr)
