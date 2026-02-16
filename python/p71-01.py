#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from pathlib import Path
from tqdm import tqdm
from typing import Optional, Iterable, List, Tuple
import argparse
import sys, os, base58, random

target='1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU'
range_lo=0x400000000000000000
range_hi=0x800000000000000000
size=2**20
workers = 28

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
	hdwallet.from_private_key(private_key=line)
	a=f"{hdwallet.address('P2PKH')}"
	if a==target:
		return f'{line}:{a}'
	else:
		return None

def gen():
	while True:
		x=random.randint(range_lo, range_hi-size)
		print(f'{hex(x)}:{hex(x+size)}')
		for i in range(x, x+size):
			yield hex(i)[2:].zfill(64)

def main():
	with Pool(processes=workers) as p:
		for result in p.imap_unordered(process_line, gen(), chunksize=1000):
			if result:
				with open('output.txt', 'a') as o:
					o.write(result+'\n')
				print(result+'\a')
				exit()

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
