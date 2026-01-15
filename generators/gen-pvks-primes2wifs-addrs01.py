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

def process_line(line) -> Optional[str]:
	x, y = line
	if hdwallet is None:
		return None
	hdwallet.from_private_key(private_key=x)
	wif = pvk_to_wif2(x)
	a = (
		f"{x}\n"
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
	hdwallet.from_private_key(private_key=y)
	wif = pvk_to_wif2(y)
	b = (
		f"{y}\n"
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
	return a, b

a=2**20

def in_path():
	for i in range(1, a):
		yield hex((6*i)-1)[2:].zfill(64), hex((6*i)+1)[2:].zfill(64)

def main():
	with open('output.txt', 'w'):
		pass

	total = a
	pbar = tqdm(
		total=total,
		unit_scale=True,
		ncols=132
	)

	workers = 24

	with Pool(processes=workers) as p, tqdm(total=total, unit_scale=True) as pbar:
		for result in p.imap_unordered(process_line, in_path(), chunksize=1000):
			a1, a2 = result
			with open('output.txt', 'a') as o:
				o.write(a1)
				o.write(a2)
			pbar.update(1)

	pbar.close()
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
