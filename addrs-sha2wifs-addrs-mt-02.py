#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.hds import BIP84HD
from hdwallet.mnemonics import BIP39Mnemonic
from tqdm.contrib.concurrent import process_map
from tqdm import tqdm
import sys, hashlib, base58
from multiprocessing import Pool

print('Reading...', flush=True)
lines=open("input.txt","rb").read().splitlines()

o = open("output.txt","w")

def shahex(x):
	return hashlib.sha256(x).hexdigest()

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(x):
	s=base58.b58decode_check(x)
	s=shahex(s)
	try:
		hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=s)
	except:
		return
	wif = pvk_to_wif2(s)

	w=f'{wif}\n{hdwallet.wif()}\n{hdwallet.address("P2PKH")}\n{hdwallet.address("P2SH")}\n{hdwallet.address("P2TR")}\n{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'

	o.write(w)
	o.flush()

th=16
max_=len(lines)
cnt=1000

print('Writing...', flush=True)

if __name__=='__main__':
	i=0
	with Pool(processes=th) as p, tqdm(total=max_) as pbar:
		for result in p.imap(go, lines):
			if i%cnt==0:
				pbar.update(cnt)
				pbar.refresh()
			i=i+1

print('\a', end='', file=sys.stderr)
