#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import sys, base58, os, re, hashlib, math

tmp = 0
cnt = 1e4
th=24
i=0
r=range(1,2**32)
l=len(r)

outfile = open('output.txt','w')

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def int_to_bytes3(value, length = None): # in: int out: bytearray(b'\x80...
	if not length and value == 0:
		result = [0]
	else:
		result = []
		for i in range(0, length or 1+int(math.log(value, 2**8))):
			result.append(value >> (i * 8) & 0xff)
		result.reverse()
	return bytearray(result)

def go(x):
	t=int_to_bytes3(x)
	u=hashlib.sha256(t).hexdigest()
	hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD).from_private_key(private_key=u)
	wif=pvk_to_wif2(u)
	a=f'{wif}\n{hdwallet.wif()}\n{hdwallet.address("P2PKH")}\n{hdwallet.address("P2SH")}\n{hdwallet.address("P2TR")}\n{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'
	outfile.write(a)

with Pool(processes=th) as p, tqdm(total=l) as pbar:
	for result in p.imap_unordered(go, r, chunksize=1000):
		i=i+1
		if i>=cnt:
			outfile.flush()
			pbar.update(i)
			pbar.refresh()
			i=0

print('\a', end='', file=sys.stderr)
