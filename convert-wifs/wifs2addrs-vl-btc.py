#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from multiprocessing import Pool, cpu_count
from pathlib import Path
from tqdm import tqdm
from typing import Optional, Iterable, List
import argparse
import sys
import os

_IS_WIN = os.name == "nt"
if _IS_WIN:
	import msvcrt
else:
	import fcntl

# Per-worker HDWallet instance stored in a plain global after Pool initializer runs.
_worker_hw = None

def _worker_init():
	global _worker_hw
	try:
		from hdwallet import HDWallet
		from hdwallet.cryptocurrencies import Bitcoin as BTC
		from hdwallet.hds import BIP32HD
		_worker_hw = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	except Exception:
		_worker_hw = None

def _lock_file(f):
	if _IS_WIN:
		try:
			msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 0x7FFFFFFF)
		except OSError:
			msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 0x7FFFFFFF)
	else:
		fcntl.flock(f.fileno(), fcntl.LOCK_EX)

def _unlock_file(f):
	if _IS_WIN:
		try:
			msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 0x7FFFFFFF)
		except OSError:
			pass
	else:
		fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def process_line(line: str) -> Optional[str]:
	line = line.rstrip('\n')
	if not line:
		return None
	hw = _worker_hw
	if hw is None:
		return None
	try:
		hw.from_wif(wif=line)
	except Exception:
		return None
	a = (
		f"{hw.wif(wif_type='wif')}\n"
		f"{hw.wif(wif_type='wif-compressed')}\n"
		f"{hw.address('P2PKH')}\n"
		f"{hw.address('P2SH')}\n"
		f"{hw.address('P2TR')}\n"
		f"{hw.address('P2WPKH')}\n"
		f"{hw.address('P2WPKH-In-P2SH')}\n"
		f"{hw.address('P2WSH')}\n"
		f"{hw.address('P2WSH-In-P2SH')}\n\n"
	)
	return a

def count_lines(file_path: Path) -> int:
	count = 0
	with file_path.open('r', encoding='utf-8', errors='replace') as f:
		for _ in f:
			count += 1
	return count

def read_lines(file_path: Path, chunk_size: int = 10000) -> Iterable[list]:
	with file_path.open('r', encoding='utf-8', errors='replace') as f:
		while True:
			chunk: List[str] = []
			for _ in range(chunk_size):
				line = f.readline()
				if not line:
					break
				chunk.append(line)
			if not chunk:
				break
			yield chunk

def write_results(results: Iterable[Optional[str]], out_path: Path, fsync: bool = True) -> None:
	filtered = [r for r in results if r is not None]
	if not filtered:
		return
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with out_path.open('a', encoding='utf-8', buffering=1) as f:
		_lock_file(f)
		try:
			for r in filtered:
				f.write(r)
			f.flush()
			if fsync:
				os.fsync(f.fileno())
		finally:
			_unlock_file(f)

def main():
	parser = argparse.ArgumentParser(description="WIF input -> addresses -> append to output")
	parser.add_argument('-i', '--input',   type=str, default='input.txt',  help='input file path')
	parser.add_argument('-o', '--output',  type=str, default='output.txt', help='output file path')
	parser.add_argument('-w', '--workers', type=int, default=30,           help='number of processes (1 = no multiprocessing)')
	parser.add_argument('-c', '--chunk',   type=int, default=10000,        help='lines per chunk')
	parser.add_argument('--no-fsync',      action='store_true',            help='disable fsync after each chunk')
	args = parser.parse_args()

	in_path  = Path(args.input)
	out_path = Path(args.output)

	if not in_path.exists():
		print(f"Input file not found: {in_path}", file=sys.stderr)
		sys.exit(1)

	out_path.parent.mkdir(parents=True, exist_ok=True)
	# Clear output once at start.
	out_path.write_text('', encoding='utf-8')

	total_lines = count_lines(in_path)
	pbar = tqdm(total=total_lines, unit='lines', ncols=132)

	workers = min(max(1, args.workers), cpu_count())

	if workers == 1:
		_worker_init()
		for chunk in read_lines(in_path, args.chunk):
			results = [process_line(line) for line in chunk]
			write_results(results, out_path, fsync=not args.no_fsync)
			pbar.update(len(chunk))
	else:
		with Pool(processes=workers, initializer=_worker_init) as pool:
			for chunk in read_lines(in_path, args.chunk):
				results = pool.map(process_line, chunk)
				write_results(results, out_path, fsync=not args.no_fsync)
				pbar.update(len(chunk))

	pbar.close()
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
