#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys, base58
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import Optional, Iterable
from tqdm import tqdm
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic

hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def process_line(line: str) -> Optional[str]:
	# TODO: put your custom per-line logic here
	line = line.rstrip('\n')
	#try:
	hdwallet.from_private_key(private_key=line)
	#except:
	#	return None
	wif=pvk_to_wif2(line)
	a = f'{line}\n{wif}\n{hdwallet.wif()}\n{hdwallet.address("P2PKH")}\n{hdwallet.address("P2SH")}\n{hdwallet.address("P2TR")}\n{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'
	return a

def _worker_wrapper(line: str) -> Optional[str]:
	#try:
	return process_line(line)
	#except Exception:
	#	return None

def count_lines(file_path: Path) -> int:
	with file_path.open('r', encoding='utf-8', errors='replace') as f:
		for i, _ in enumerate(f, 1):
			pass
	return i if 'i' in locals() else 0

def read_lines(file_path: Path, chunk_size: int = 10000) -> Iterable[list]:
	with file_path.open('r', encoding='utf-8', errors='replace') as f:
		while True:
			chunk = []
			for _ in range(chunk_size):
				l = f.readline()
				if not l:
					break
				chunk.append(l)
			if not chunk:
				break
			yield chunk

def write_results(results: Iterable[str], out_path: Path) -> None:
	if not results:
		return
	with out_path.open('a', encoding='utf-8') as f:
		for r in results:
			if r is not None:
				f.write(r)

def main():
	parser = argparse.ArgumentParser(description="Template: read lines -> process_line -> write output")
	parser.add_argument('-i','--input', type=str, default='input.txt', help='input file path')
	parser.add_argument('-o','--output', type=str, default='output.txt', help='output file path')
	parser.add_argument('-w','--workers', type=int, default=16, help='number of processes (1 = no multiprocessing)')
	parser.add_argument('-c','--chunk', type=int, default=10000, help='number of lines per chunk')
	args = parser.parse_args()

	in_path = Path(args.input)
	out_path = Path(args.output)

	if not in_path.exists():
		sys.exit(1)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	out_path.write_text('', encoding='utf-8')

	total_lines = count_lines(in_path)
	pbar = tqdm(total=total_lines, unit='lines', ncols=80)

	workers = max(1, args.workers)
	if workers > cpu_count():
		workers = cpu_count()

	if workers == 1:
		for chunk in read_lines(in_path, args.chunk):
			results = []
			for line in chunk:
				r = _worker_wrapper(line)
				if r is not None:
					results.append(r)
			write_results(results, out_path)
			pbar.update(len(chunk))
	else:
		with Pool(processes=workers) as pool:
			for chunk in read_lines(in_path, args.chunk):
				results = pool.map(_worker_wrapper, chunk)
				write_results(results, out_path)
				pbar.update(len(chunk))
	pbar.close()
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
