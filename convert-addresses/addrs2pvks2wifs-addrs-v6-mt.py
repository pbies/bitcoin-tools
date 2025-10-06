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
open('output.txt','w').close()

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(k):
	try:
		k=base58.b58decode_check(k).hex()[2:].zfill(64)
		hdwallet.from_private_key(k)
	except Exception as e:
		return
	wif=pvk_to_wif2(k)
	w=f'{k}\n{wif}\n{hdwallet.wif()}\n{hdwallet.address("P2PKH")}\n{hdwallet.address("P2SH")}\n{hdwallet.address("P2TR")}\n{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'
	with open('output.txt','a') as outfile:
		outfile.write(w)

print('Writing...', flush=True)
process_map(go, infile, max_workers=24, chunksize=1000)

print('\a', end='', file=sys.stderr)
