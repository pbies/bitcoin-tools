#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import sys, base58, hashlib

hdwallet = HDWallet(symbol=BTC)

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def shahex(x):
	return hashlib.sha256(x).hexdigest()

def go(k):
	i=bytes.fromhex(k)
	s=shahex(i)
	try:
		hdwallet.from_private_key(private_key=s)
	except:
		return
	wif=pvk_to_wif2(k)
	a=wif+'\n'+hdwallet.wif()+'\n'+hdwallet.p2pkh_address()+'\n'+hdwallet.p2sh_address()+'\n'+hdwallet.p2wpkh_address()+'\n'+hdwallet.p2wpkh_in_p2sh_address()+'\n'+hdwallet.p2wsh_address()+'\n'+hdwallet.p2wsh_in_p2sh_address()+'\n\n'
	outfile.write(a)
	outfile.flush()

print('Reading...', flush=True)
infile = open('input.txt','r')
lines = infile.read().splitlines()

print('Writing...', flush=True)
outfile = open('output.txt','w')
process_map(go, lines, max_workers=16, chunksize=1000)

print('\a', end='', file=sys.stderr)
