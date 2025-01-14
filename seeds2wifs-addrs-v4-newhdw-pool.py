#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP84HD
from hdwallet.mnemonics import BIP39Mnemonic
from hdwallet.seeds import BIP39Seed
from multiprocessing import Pool
from pprint import pprint
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import pprint
import random

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP84HD)

def go(k):
	try:
		hdwallet.from_seed(seed=BIP39Seed(k))
	except:
		return
	pvk=hdwallet.private_key()
	wif=pvk_to_wif2(pvk)
	w=f'{wif}\n{hdwallet.wif()}\n{hdwallet.address("P2PKH")}\n{hdwallet.address("P2SH")}\n{hdwallet.address("P2TR")}\n{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'
	outfile.write(w)
	outfile.flush()

infile = open('input.txt','r')
outfile = open('output.txt','w')

print('Reading...')
lines = infile.read().splitlines()

th=16
max_=len(lines)

print('Writing...')

if __name__=='__main__':
	i=0
	with Pool(processes=th) as p, tqdm(total=max_) as pbar:
		for result in p.imap(go, lines):
			if i%1000==0:
				pbar.update(1000)
				pbar.refresh()
			i=i+1

import sys
print('\a', end='', file=sys.stderr)
