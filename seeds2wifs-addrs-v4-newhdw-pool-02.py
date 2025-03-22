#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
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

def go(k):
	try:
		hdwallet1 = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_seed(seed=BIP39Seed(k))
		hdwallet2 = HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_seed(seed=BIP39Seed(k))
	except:
		return
	pvk1=hdwallet1.private_key()
	pvk2=hdwallet2.private_key()
	wif1=pvk_to_wif2(pvk1)
	wif2=pvk_to_wif2(pvk2)
	w=f'{wif1}\n{hdwallet1.wif()}\n{hdwallet1.address("P2PKH")}\n{hdwallet1.address("P2SH")}\n{hdwallet1.address("P2TR")}\n{hdwallet1.address("P2WPKH")}\n{hdwallet1.address("P2WPKH-In-P2SH")}\n{hdwallet1.address("P2WSH")}\n{hdwallet1.address("P2WSH-In-P2SH")}\n\n'
	w=w+f'{wif2}\n{hdwallet2.wif()}\n{hdwallet2.address("P2PKH")}\n{hdwallet2.address("P2SH")}\n{hdwallet2.address("P2TR")}\n{hdwallet2.address("P2WPKH")}\n{hdwallet2.address("P2WPKH-In-P2SH")}\n{hdwallet2.address("P2WSH")}\n{hdwallet2.address("P2WSH-In-P2SH")}\n\n'
	outfile.write(w)
	outfile.flush()

infile = open('input.txt','r')
outfile = open('output.txt','w')

print('Reading...', flush=True)
lines = infile.read().splitlines()

th=16
max_=len(lines)
cnt = 1000

print('Writing...', flush=True)

if __name__=='__main__':
	i=0
	with Pool(processes=th) as p, tqdm(total=max_) as pbar:
		for result in p.imap(go, lines):
			if i%cnt==0:
				pbar.update(cnt)
				pbar.refresh()
			i=i+1

import sys
print('\a', end='', file=sys.stderr)
