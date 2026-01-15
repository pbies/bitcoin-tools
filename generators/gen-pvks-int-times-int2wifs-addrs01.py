#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from multiprocessing import Pool, cpu_count
from pathlib import Path
from tqdm import tqdm
from typing import Optional, Iterable, List, Tuple
import argparse
import sys, os, base58

try:
	from hdwallet import HDWallet
	from hdwallet.cryptocurrencies import Bitcoin as BTC
	from hdwallet.hds import BIP32HD
	hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
except Exception:
	hdwallet = None

def pvk_to_wif2(key_hex: str) -> str:
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def process_line(line: str) -> Optional[str]:
	if hdwallet is None:
		return None
	hdwallet.from_private_key(private_key=line)
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

a=1025
b=1025

def in_path():
	for i in range(1, a):
		for j in range(i, b):
			yield hex(i*j)[2:].zfill(64)

def main():
	with open('output.txt', 'w'):
		pass

	total = a*b//2
	pbar = tqdm(
		total=total,
		unit_scale=True,
		ncols=132
	)

	workers = 24

	with Pool(processes=workers) as p, tqdm(total=total, unit_scale=True) as pbar:
		for result in p.imap_unordered(process_line, in_path(), chunksize=1000):
			with open('output.txt', 'a') as o:
				o.write(result)
			pbar.update(1)

	pbar.close()
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
