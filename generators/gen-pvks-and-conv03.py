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
import sys, base58, os

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(k):
	try:
		hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=k)
	except:
		return
	wif=pvk_to_wif2(k)
	a=k+'\n'+wif+'\n'+hdwallet.wif()+'\n'+hdwallet.address("P2PKH")+'\n'+hdwallet.address("P2SH")+'\n'+hdwallet.address("P2TR")+'\n'+hdwallet.address("P2WPKH")+'\n'+hdwallet.address("P2WPKH-In-P2SH")+'\n'+hdwallet.address("P2WSH")+'\n'+hdwallet.address("P2WSH-In-P2SH")+'\n\n'
	outfile.write(a)

outfile = open('output.txt','w')

a=[]

for i in tqdm(range(1,265)):
	x=2**i
	#print(hex(x))
	for j in range(-1024, 1025):
		y=x+j
		h=hex(y)[2:].zfill(64)
		#print(h)
		a.append(h)

b=list(set(a))
b.sort()

for i in tqdm(b):
	go(i)

print('\a', end='', file=sys.stderr)
