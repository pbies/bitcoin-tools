#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import sys, base58

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(k):
	try:
		b=base58.b58decode_check(k)
		h=b.hex()
		h='0'*(64-len(h))+h
		hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=h)
	except:
		return
	wif=pvk_to_wif2(h)
	a=wif+'\n'+hdwallet.wif()+'\n'+hdwallet.address("P2PKH")+'\n'+hdwallet.address("P2SH")+'\n'+hdwallet.address("P2TR")+'\n'+hdwallet.address("P2WPKH")+'\n'+hdwallet.address("P2WPKH-In-P2SH")+'\n'+hdwallet.address("P2WSH")+'\n'+hdwallet.address("P2WSH-In-P2SH")+'\n\n'
	outfile.write(a)
	outfile.flush()

print('Reading...', flush=True)
infile = open('input.txt','r')
lines = infile.read().splitlines()

print('Writing...', flush=True)
outfile = open('output.txt','w')
process_map(go, lines, max_workers=16, chunksize=1000)

print('\a', end='', file=sys.stderr)
