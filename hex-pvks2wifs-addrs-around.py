#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.entropies import BIP39Entropy
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from hdwallet.seeds import BIP39Seed
from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import sys, os

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

infile = open('input.txt','r')
i=infile.tell()
tmp = 0
cnt = 1000

def go(k):
	global tmp, i
	x=k.rstrip('\n')
	y=int(x, 16)

	for z in range(y-100, y+100):
		k=hex(z)[2:].zfill(64)
		try:
			hdwallet=HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=k)
		except:
			continue

		pvk=hdwallet.private_key()
		wif=pvk_to_wif2(pvk)
		r=f'{wif}\n{hdwallet.wif()}\n{hdwallet.address("P2PKH")}\n{hdwallet.address("P2SH")}\n{hdwallet.address("P2TR")}\n{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'
		outfile.write(r)
		outfile.flush()
		i=infile.tell()
		r=i-tmp
		if r>cnt:
			tmp=i
			pbar.update(r)
			pbar.refresh()

#infile = open('input.txt','r')
outfile = open('output.txt','w')
size = os.path.getsize('input.txt')

if __name__=='__main__':
	th=16
	i=0
	pbar=tqdm(total=size)
	with Pool(processes=th) as p, tqdm(total=size) as pbar:
		for result in p.imap_unordered(go, infile, chunksize=1000):
			pass

	print('\a', end='', file=sys.stderr)
