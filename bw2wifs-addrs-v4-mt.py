#!/usr/bin/env python3

from hdwallet import HDWallet
#from hdwallet.symbols import BTC
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from tqdm.contrib.concurrent import process_map
import hashlib, base58
import sys

hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

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
	outfile.write(hdwallet.address("P2PKH")+'\n')
	outfile.write(hdwallet.address("P2SH")+'\n')
	outfile.write(hdwallet.address("P2TR")+'\n')
	outfile.write(hdwallet.address("P2WPKH")+'\n')
	outfile.write(hdwallet.address("P2WPKH-In-P2SH")+'\n')
	outfile.write(hdwallet.address("P2WSH")+'\n')
	outfile.write(hdwallet.address("P2WSH-In-P2SH")+'\n\n')
	outfile.flush()

print('Writing...', flush=True)
process_map(go, infile, max_workers=16, chunksize=1000)

print('\a', end='', file=sys.stderr)
