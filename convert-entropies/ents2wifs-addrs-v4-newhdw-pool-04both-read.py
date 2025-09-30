#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.hds import BIP84HD
from hdwallet.mnemonics import BIP39Mnemonic
from hdwallet.seeds import BIP39Seed
from hdwallet.entropies import BIP39Entropy
from multiprocessing import Pool
from pprint import pprint
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import pprint
import random
import os
import sys
import math

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(k):
	try:
		hdwallet1 = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_entropy(entropy=BIP39Entropy(k))
		hdwallet2 = HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_entropy(entropy=BIP39Entropy(k))
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

cnt = 1000
size = os.path.getsize('input.txt')
i=infile.tell()
tmp = 0

if __name__=='__main__':
	pbar = tqdm(total=size)
	while True:
		line=infile.readline()
		if not line:
			break
		go(line)
		i=infile.tell()
		r=i-tmp
		if r>cnt:
			tmp=i
			pbar.update(r)
			pbar.refresh()
	print()

	print('\a', end='', file=sys.stderr)
 