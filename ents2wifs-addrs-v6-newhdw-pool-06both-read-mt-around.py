#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.entropies import BIP39Entropy
from hdwallet.hds import BIP32HD
from multiprocessing import Pool
from tqdm import tqdm
import base58
import hashlib
import os
import sys

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

infile = open('input.txt','rb')
i=infile.tell()
tmp = 0
cnt = 100
OFFSETS = [-65536, -65535, -31337, -1000, -100, -64, 0, 1, 64, 100, 1000, 31337, 65535, 65536]

def go(x):
	x=x[:-1].decode()
	h=int(x,16)
	for z in OFFSETS:
		y=hex(h+z)[2:].zfill(32)
		try:
			hdwallet1 = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_entropy(entropy=BIP39Entropy(y))
		except:
			#print(f'Error with: {x}')
			return
		pvk1=hdwallet1.private_key()
		wif1=pvk_to_wif2(pvk1)
		w=f'{y}\n{wif1}\n{hdwallet1.wif()}\n{hdwallet1.address("P2PKH")}\n{hdwallet1.address("P2SH")}\n{hdwallet1.address("P2TR")}\n{hdwallet1.address("P2WPKH")}\n{hdwallet1.address("P2WPKH-In-P2SH")}\n{hdwallet1.address("P2WSH")}\n{hdwallet1.address("P2WSH-In-P2SH")}\n\n'
		outfile.write(w)
		outfile.flush()

outfile = open('output.txt','w')

size = os.path.getsize('input.txt')
th=4

if __name__=='__main__':
	pbar=tqdm(total=size)
	with Pool(processes=th) as p, tqdm(total=size, unit='B', unit_scale=True) as pbar:
		for result in p.imap_unordered(go, infile, chunksize=10):
			i=infile.tell()
			r=i-tmp
			if r>cnt:
				tmp=i
				pbar.update(r)
				pbar.refresh()

	print('\a', end='', file=sys.stderr)
