#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import sys, base58

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(k):
	try:
		hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=k)
	except:
		return
	wif=pvk_to_wif2(k)
	a=wif+'\n'+hdwallet.wif()+'\n'+hdwallet.address("P2PKH")+'\n'+hdwallet.address("P2SH")+'\n'+hdwallet.address("P2TR")+'\n'+hdwallet.address("P2WPKH")+'\n'+hdwallet.address("P2WPKH-In-P2SH")+'\n'+hdwallet.address("P2WSH")+'\n'+hdwallet.address("P2WSH-In-P2SH")+'\n\n'
	outfile.write(a)

print('Reading...', flush=True)
infile = open('input.txt','r')
lines = infile.read().splitlines()

th=24
max_=len(lines)

print('Writing...', flush=True)
outfile = open('output.txt','w')
i=0
with Pool(processes=th) as p, tqdm(total=max_) as pbar:
	for result in p.imap_unordered(go, lines, chunksize=1000):
		if i%1000==0:
			outfile.flush()
			pbar.update(1000)
			pbar.refresh()
		i=i+1

print('\a', end='', file=sys.stderr)
