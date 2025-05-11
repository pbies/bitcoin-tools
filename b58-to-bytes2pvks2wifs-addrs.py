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
	#k=k.decode()
	p=base58.b58decode_check(k)
	q=p.hex().zfill(64)
	#print(q)
	try:
		hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=q)
	except:
		return
	wif=pvk_to_wif2(q)
	a=wif+'\n'+hdwallet.wif()+'\n'+hdwallet.address("P2PKH")+'\n'+hdwallet.address("P2SH")+'\n'+hdwallet.address("P2TR")+'\n'+hdwallet.address("P2WPKH")+'\n'+hdwallet.address("P2WPKH-In-P2SH")+'\n'+hdwallet.address("P2WSH")+'\n'+hdwallet.address("P2WSH-In-P2SH")+'\n\n'
	outfile.write(a)

infile = open('input.txt','rb')
size = os.path.getsize('input.txt')
outfile = open('output.txt','w')

th=24
cnt=1e6
tmp=0

with Pool(processes=th) as p, tqdm(total=size, unit='B', unit_scale=True) as pbar:
	for result in p.imap_unordered(go, infile, chunksize=1000):
		pos=infile.tell()
		r=pos-tmp
		if r>cnt:
			outfile.flush()
			tmp=pos
			pbar.update(r)
			pbar.refresh()

print('\a', end='', file=sys.stderr)
