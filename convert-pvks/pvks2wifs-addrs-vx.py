#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from multiprocessing import Pool, cpu_count
from pathlib import Path
from tqdm import tqdm
from typing import Optional, Iterable, List, Tuple
import argparse
import sys, os, base58

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD

hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def pvk_to_wif2(key_hex: str) -> str:
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def process_line(line: str) -> Optional[str]:
	line = line.rstrip('\n')
	try:
		hdwallet.from_private_key(private_key=line)
	except Exception:
		return None
	#wif = pvk_to_wif2(line)
	a = (
		f"{line}\n"
		f"{hdwallet.wif(wif_type='wif')}\n"
		f"{hdwallet.wif(wif_type='wif-compressed')}\n"
		f"{hdwallet.address('P2PKH')}\n"
		f"{hdwallet.address('P2SH')}\n"
		f"{hdwallet.address('P2TR')}\n"
		f"{hdwallet.address('P2WPKH')}\n"
		f"{hdwallet.address('P2WPKH-In-P2SH')}\n"
		f"{hdwallet.address('P2WSH')}\n"
		f"{hdwallet.address('P2WSH-In-P2SH')}\n\n"
	)
	return a

def read_lines_bytes_progress(file_path: Path, chunk_size: int = 10000) -> Iterable[Tuple[List[str], int]]:
	"""
	Stream read in binary mode so tell() is reliable.
	Yields: (chunk_lines_as_str, file_pos_in_bytes_after_read)
	"""
	with file_path.open('rb') as f:
		while True:
			chunk: List[str] = []
			for _ in range(chunk_size):
				b = f.readline()
				if not b:
					break
				# input looks like hex; keep it simple and robust
				chunk.append(b.decode('utf-8', errors='replace'))
			if not chunk:
				break
			yield chunk, f.tell()

def write_results(results: Iterable[str], out_path: Path, fsync: bool = True) -> None:
	if not results:
		return
	out_path.parent.mkdir(parents=True, exist_ok=True)
	while True:
		try:
			with out_path.open('a', encoding='utf-8', buffering=1) as f:
				try:
					for r in results:
						if r is not None:
							f.write(r)
					f.flush()
					if fsync:
						os.fsync(f.fileno())
				finally:
					return
		except:
			pass

def main():
	parser = argparse.ArgumentParser(description="Stream input; progress by bytes read from input file position")
	parser.add_argument('-i','--input', type=str, default='input.txt', help='input file path')
	parser.add_argument('-o','--output', type=str, default='output.txt', help='output file path')
	parser.add_argument('-w','--workers', type=int, default=28, help='number of processes (1 = no multiprocessing)')
	parser.add_argument('-c','--chunk', type=int, default=10000, help='number of lines per chunk')
	parser.add_argument('--no-fsync', action='store_true', help='disable fsync() after each chunk to improve speed')
	args = parser.parse_args()

	in_path = Path(args.input)
	out_path = Path(args.output)

	if not in_path.exists():
		sys.exit(1)

	# Truncate/create output file once
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with out_path.open('w', encoding='utf-8') as f:
		pass

	total_bytes = in_path.stat().st_size
	pbar = tqdm(
		total=total_bytes,
		unit='B',
		unit_scale=True,
		unit_divisor=1024,
		ncols=132
	)

	workers = max(1, args.workers)
	if workers > cpu_count():
		workers = cpu_count()

	last_pos = 0

	if workers == 1:
		for chunk, pos in read_lines_bytes_progress(in_path, args.chunk):
			results = []
			for line in chunk:
				r = process_line(line)
				if r is not None:
					results.append(r)
			write_results(results, out_path, fsync=not args.no_fsync)
			delta = pos - last_pos
			if delta > 0:
				pbar.update(delta)
			last_pos = pos
	else:
		with Pool(processes=workers) as pool:
			for chunk, pos in read_lines_bytes_progress(in_path, args.chunk):
				results = pool.map(process_line, chunk)
				write_results(results, out_path, fsync=not args.no_fsync)
				delta = pos - last_pos
				if delta > 0:
					pbar.update(delta)
				last_pos = pos

	# domknij do 100% jeśli system/FS zwrócił nietypowe wartości tell()
	if last_pos < total_bytes:
		pbar.update(total_bytes - last_pos)

	pbar.close()
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
