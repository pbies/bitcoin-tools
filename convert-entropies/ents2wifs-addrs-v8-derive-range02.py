#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys, base58
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import Optional, Iterable, Iterator, Tuple, List
from tqdm import tqdm
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
import bip32utils

# Note: avoid sharing HDWallet instances across processes.
def pvk_to_wif2(key_hex: str) -> str:
	# Legacy helper kept for compatibility
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def bip39(seed: bytes, x: int, y: int) -> str:
	bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed)
	# Derivation: m/84'/0'/0'/x/y
	bip32_child_key_obj = (
		bip32_root_key_obj
		.ChildKey(84 + bip32utils.BIP32_HARDEN)
		.ChildKey(0 + bip32utils.BIP32_HARDEN)
		.ChildKey(0 + bip32utils.BIP32_HARDEN)
		.ChildKey(int(x))
		.ChildKey(int(y))
	)
	return bip32_child_key_obj.WalletImportFormat()

def derive_one(job: Tuple[str, int, int]) -> Optional[str]:
	seed_hex, x, y = job
	seed_hex = seed_hex.rstrip('\n')
	if not seed_hex:
		return None
	try:
		wif = bip39(bytes.fromhex(seed_hex), x, y)
		hd = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
		hd.from_wif(wif)
		out = (
			f"{seed_hex}/{x}/{y}\n"
			f"{wif}\n"
			f"{hd.address('P2PKH')}\n"
			f"{hd.address('P2SH')}\n"
			f"{hd.address('P2TR')}\n"
			f"{hd.address('P2WPKH')}\n"
			f"{hd.address('P2WPKH-In-P2SH')}\n"
			f"{hd.address('P2WSH')}\n"
			f"{hd.address('P2WSH-In-P2SH')}\n\n"
		)
		return out
	except Exception:
		return None

def count_lines(file_path: Path) -> int:
	with file_path.open('r', encoding='utf-8', errors='replace') as f:
		for i, _ in enumerate(f, 1):
			pass
	return i if 'i' in locals() else 0

def job_generator(file_path: Path, x_max: int = 4, y_max: int = 1025) -> Iterator[Tuple[str, int, int]]:
	with file_path.open('r', encoding='utf-8', errors='replace') as f:
		for line in f:
			seed = line.strip()
			if not seed:
				continue
			for x in range(x_max):
				for y in range(y_max):
					yield (seed, x, y)

def write_buffered(buffer: List[str], out_path: Path) -> None:
	if not buffer:
		return
	with out_path.open('a', encoding='utf-8') as f:
		for r in buffer:
			if r is not None:
				f.write(r)
	buffer.clear()

def main():
	parser = argparse.ArgumentParser(description="Parallel derivation: distribute (x,y) loops across processes")
	parser.add_argument('-i','--input', type=str, default='input.txt', help='input file path')
	parser.add_argument('-o','--output', type=str, default='output.txt', help='output file path')
	parser.add_argument('-w','--workers', type=int, default=24, help='number of processes (1 = no multiprocessing)')
	parser.add_argument('--xmax', type=int, default=4, help='exclusive upper bound for x')
	parser.add_argument('--ymax', type=int, default=1025, help='exclusive upper bound for y')
	parser.add_argument('--chunksize', type=int, default=128, help='chunksize for imap_unordered')
	parser.add_argument('--buf', type=int, default=1000, help='write buffer size')
	args = parser.parse_args()

	in_path = Path(args.input)
	out_path = Path(args.output)

	if not in_path.exists():
		sys.exit(1)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	out_path.write_text('', encoding='utf-8')

	total_lines = count_lines(in_path)
	total_tasks = total_lines * args.xmax * args.ymax
	pbar = tqdm(total=total_tasks, unit='deriv', ncols=132)

	workers = max(1, args.workers)
	if workers > cpu_count():
		workers = cpu_count()

	if workers == 1:
		buf: List[str] = []
		for job in job_generator(in_path, args.xmax, args.ymax):
			res = derive_one(job)
			if res is not None:
				buf.append(res)
			if len(buf) >= args.buf:
				write_buffered(buf, out_path)
			pbar.update(1)
		write_buffered(buf, out_path)
	else:
		with Pool(processes=workers) as pool:
			buf: List[str] = []
			for res in pool.imap_unordered(
				derive_one,
				job_generator(in_path, args.xmax, args.ymax),
				chunksize=max(1, args.chunksize)
			):
				if res is not None:
					buf.append(res)
				if len(buf) >= args.buf:
					write_buffered(buf, out_path)
				pbar.update(1)
			write_buffered(buf, out_path)

	pbar.close()
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
