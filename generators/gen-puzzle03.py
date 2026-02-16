#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from pathlib import Path
from tqdm import tqdm
from typing import Optional, Iterable, List, Tuple
import argparse
import sys, os, base58, random

try:
	from hdwallet import HDWallet
	from hdwallet.cryptocurrencies import Bitcoin as BTC
	from hdwallet.hds import BIP32HD
	hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
except Exception:
	hdwallet = None

def pvk_to_wif2(key_hex: str) -> str:
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(line):
	try:
		hdwallet.from_private_key(private_key=line)
	except:
		return ''
	wif = pvk_to_wif2(line)
	a = (
		f"{line}\n"
		f"{wif}\n"
		f"{hdwallet.wif()}\n"
		f"{hdwallet.address('P2PKH')}\n"
		f"{hdwallet.address('P2SH')}\n"
		f"{hdwallet.address('P2TR')}\n"
		f"{hdwallet.address('P2WPKH')}\n"
		f"{hdwallet.address('P2WPKH-In-P2SH')}\n"
		f"{hdwallet.address('P2WSH')}\n"
		f"{hdwallet.address('P2WSH-In-P2SH')}\n\n"
	)
	return a

def main():
	o=open('output.txt','w')
	p=open('output2.txt','w')
	for i in tqdm(range(0, 65537)):
		random.seed(i)
		s=set()
		for j in range(0, 256):
			t=hex(random.randint(2**j, 2**(j+1)))[2:].zfill(64)
			s.add(t)
			o.write(t+'\n')
			p.write(go(t))
		o.write('\n')
		p.write('\n')
		o.flush()
		p.flush()

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
