#!/usr/bin/env python3

from ecdsa import SigningKey, SECP256k1
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58, re
import os, sys, hashlib

hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
order = SECP256k1.order

def pvk_to_wif(key_bytes):
	return base58.b58encode_check(b'\x80' + key_bytes)

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def entropy_to_pvk(e):
	entropy_int = int(e, 16)
	if entropy_int >= order or entropy_int < 1:
		return None
	private_key = SigningKey.from_secret_exponent(entropy_int, curve=SECP256k1)
	private_key_bytes = private_key.to_string()
	return private_key_bytes.hex()

def go(k):
	p=entropy_to_pvk(k)
	if p==None:
		return
	try:
		w=pvk_to_wif2(p)
		hdwallet.from_private_key(p)
	except:
		return
	r=f'{w}\n{hdwallet.wif()}\n{hdwallet.address("P2PKH")}\n{hdwallet.address("P2SH")}\n{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'
	with open('output.txt','a') as o:
		o.write(r)

print('Reading...', flush=True)
lines = open('input.txt','r').read().splitlines()

print('Writing...', flush=True)
open('output.txt', 'w').close()

c=10000
t=0

with Pool(processes=24) as p, tqdm(total=len(lines)) as pbar: # , unit='B', unit_scale=True
	for result in p.imap_unordered(go, lines, chunksize=1000):
		t=t+1
		if t==c:
			pbar.update(c)
			pbar.refresh()
			t=0

print('\a', end='', file=sys.stderr)
