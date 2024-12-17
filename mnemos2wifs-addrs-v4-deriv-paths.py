#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.derivations import CustomDerivation
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from multiprocessing import Pool
from pprint import pprint
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import pprint
import random
import sys

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(k):
	for i in range(0,4):
		for j in range(0,1026):
			try:
				hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_mnemonic(mnemonic=BIP39Mnemonic(mnemonic=k)).from_derivation(derivation=CustomDerivation(path="m/44'/0'/"+str(i)+"'/0/"+str(j)))
			except:
				return
			pvk=hdwallet.private_key()
			wif=pvk_to_wif2(pvk)
			w=wif+'\n'+hdwallet.wif()+'\n'+hdwallet.address("P2PKH")+'\n'+hdwallet.address("P2SH")+'\n'+hdwallet.address("P2TR")+'\n'+hdwallet.address("P2WPKH")+'\n'+hdwallet.address("P2WPKH-In-P2SH")+'\n'+hdwallet.address("P2WSH")+'\n'+hdwallet.address("P2WSH-In-P2SH")+'\n\n'
			outfile.write(w)
			outfile.flush()

infile = open('input.txt','r')
outfile = open('output.txt','w')

print('Reading...')
lines = infile.read().splitlines()

max_ = len(lines)
th = 20
i = 0

print('Writing...')
if __name__ == "__main__":
	with Pool(processes=th) as p, tqdm(total=max_) as pbar:
		for result in p.imap(go, lines):
			if i%100==0:
				pbar.update(100)
				pbar.refresh()
			i=i+1

print('\a', end='', file=sys.stderr)
