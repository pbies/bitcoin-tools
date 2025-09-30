#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD, BIP84HD
from hdwallet.mnemonics import BIP39Mnemonic
from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import sys, base58, os

infile = open('input.txt','rb')

size = os.path.getsize('input.txt')
tmp = 0
cnt = 100000
th=16
i=0

outfile = open('output.txt','w')

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(k):
	k=k.decode().strip()
	try:
		hdwallet1 = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=k)
		hdwallet2 = HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_private_key(private_key=k)
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

with Pool(processes=th) as p, tqdm(total=size, unit='B', unit_scale=True) as pbar:
	for result in p.imap_unordered(go, infile, chunksize=1000):
		pos=infile.tell()
		r=pos-tmp
		if r>cnt:
			tmp=pos
			pbar.update(r)
			pbar.refresh()

print('\a', end='', file=sys.stderr)
