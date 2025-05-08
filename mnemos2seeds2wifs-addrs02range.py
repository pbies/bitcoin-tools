#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.hds import BIP84HD
from hdwallet.mnemonics import BIP39Mnemonic
from hdwallet.seeds import BIP39Seed
from mnemonic import Mnemonic
from multiprocessing import Pool
from tqdm import tqdm
import base58
import os

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(k):
	mnemo=Mnemonic('english')
	seed=mnemo.to_seed(k,'').hex()
	try:
		hdwallet1 = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_seed(seed=BIP39Seed(seed))
		hdwallet2 = HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_seed(seed=BIP39Seed(seed))
	except:
		return
	pvk1=hdwallet1.private_key()
	pvk2=hdwallet2.private_key()
	t1=int(pvk1, 16)
	t2=int(pvk2, 16)
	for i in range(-3, 4):
		p1=hex(t1+i)[2:].zfill(64)
		p2=hex(t2+i)[2:].zfill(64)
		h1 = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=p1)
		h2 = HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_private_key(private_key=p2)
		wif1=pvk_to_wif2(p1)
		wif2=pvk_to_wif2(p2)
		w=f'{wif1}\n{h1.wif()}\n{h1.address("P2PKH")}\n{h1.address("P2SH")}\n{h1.address("P2TR")}\n{h1.address("P2WPKH")}\n{h1.address("P2WPKH-In-P2SH")}\n{h1.address("P2WSH")}\n{h1.address("P2WSH-In-P2SH")}\n\n'
		w=w+f'{wif2}\n{h2.wif()}\n{h2.address("P2PKH")}\n{h2.address("P2SH")}\n{h2.address("P2TR")}\n{h2.address("P2WPKH")}\n{h2.address("P2WPKH-In-P2SH")}\n{h2.address("P2WSH")}\n{h2.address("P2WSH-In-P2SH")}\n\n'
		outfile.write(w)
		outfile.flush()

infile = open('input.txt','r')
outfile = open('output.txt','w')

os.system('cls||clear')

print('Reading...', flush=True)
lines = infile.read().splitlines()

th=28
max_=len(lines)
cnt = 1000

print('Writing...', flush=True)

if __name__=='__main__':
	i=0
	with Pool(processes=th) as p, tqdm(total=max_) as pbar:
		for result in p.imap_unordered(go, lines, chunksize=1000):
			if i%cnt==0:
				pbar.update(cnt)
				pbar.refresh()
			i=i+1

import sys
print('\a', end='', file=sys.stderr)
