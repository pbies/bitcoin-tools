#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from multiprocessing import Pool
from tqdm import tqdm
import base58
import hashlib
import os
import sys

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(x):
	x=x.rstrip(b'\n')
	sha=hashlib.sha256(x).hexdigest()
	try:
		hdwallet1 = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=sha)
	except:
		return
	wif1=pvk_to_wif2(sha)
	w=f'{wif1}\n{hdwallet1.wif()}\n{hdwallet1.address("P2PKH")}\n{hdwallet1.address("P2SH")}\n{hdwallet1.address("P2TR")}\n{hdwallet1.address("P2WPKH")}\n{hdwallet1.address("P2WPKH-In-P2SH")}\n{hdwallet1.address("P2WSH")}\n{hdwallet1.address("P2WSH-In-P2SH")}\n\n'
	return w

th=24

if __name__=='__main__':
	os.system('cls' if os.name == 'nt' else 'clear')
	print('Reading...', flush=True)
	infile = open('input.txt','rb').read().splitlines()

	if os.path.exists('output.txt'):
		os.remove('output.txt')

	c=0
	cnt=1000

	print('Writing...', flush=True)
	with Pool(processes=th) as p, tqdm(total=len(infile)) as pbar:
		for result in p.imap_unordered(go, infile, chunksize=1000):
			outfile = open('output.txt','a')
			outfile.write(result)
			outfile.close()
			if c%cnt == 0:
				pbar.update(cnt)
				pbar.refresh()
			c+=1

	print('\a', end='', file=sys.stderr)
