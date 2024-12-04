#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
import hashlib, base58
import sys

hdwallet = HDWallet(symbol=BTC)

print('Reading...', flush=True)
infile = open('input.txt','rb').read().splitlines()
outfile = open('output.txt','w')

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(k):
	sha=hashlib.sha256(k).hexdigest()
	hdwallet.from_private_key(sha)
	wif=pvk_to_wif2(sha)
	outfile.write(wif+'\n')
	outfile.write(hdwallet.wif()+'\n')
	outfile.write(hdwallet.p2pkh_address()+'\n')
	outfile.write(hdwallet.p2sh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_in_p2sh_address()+'\n')
	outfile.write(hdwallet.p2wsh_address()+'\n')
	outfile.write(hdwallet.p2wsh_in_p2sh_address()+'\n\n')
	outfile.flush()

print('Writing...', flush=True)
process_map(go, infile, max_workers=16, chunksize=1000)

print('\a', end='', file=sys.stderr)
