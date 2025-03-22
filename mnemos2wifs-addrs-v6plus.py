#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.hds import BIP84HD
from hdwallet.mnemonics import BIP39Mnemonic
from multiprocessing import Pool
from tqdm import tqdm
import base58

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def hex_to_int(hex): # in: '8000... out: 32768
	return int(hex, 16)

def int_to_hex(i): # in: int out: 0x8000
	return hex(i)

def go(k):
	try:
		hdwallet1 = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_mnemonic(mnemonic=BIP39Mnemonic(mnemonic=k))
	except:
		return
	pvk1=hdwallet1.private_key()
	tmp=hex_to_int(pvk1)
	for i in range(tmp-9,tmp+101):
		target=hex(i)[2:].zfill(64)
		#print(target)
		try:
			pvk2=hdwallet1.from_private_key(target)
		except:
			continue
		wif1=pvk_to_wif2(target)
		w=f'{target}\n{wif1}\n{hdwallet1.wif()}\n{hdwallet1.address("P2PKH")}\n{hdwallet1.address("P2SH")}\n{hdwallet1.address("P2TR")}\n{hdwallet1.address("P2WPKH")}\n{hdwallet1.address("P2WPKH-In-P2SH")}\n{hdwallet1.address("P2WSH")}\n{hdwallet1.address("P2WSH-In-P2SH")}\n\n'
		outfile.write(w)
		outfile.flush()

infile = open('input.txt','r')
outfile = open('output.txt','w')

print('Reading...', flush=True)
lines = infile.read().splitlines()

th=24
max_=len(lines)
cnt = 100

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
