#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from multiprocessing import Pool, cpu_count
from pathlib import Path
from tqdm import tqdm
from typing import Optional, Iterable, List, Tuple
import argparse
import sys, os, base58, math

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD

# NOTE: do NOT create a global hdwallet here — it must be created per-process
# to avoid shared mutable state corruption in multiprocessing workers.
cur = 115792089237316195423570985008687907852837564279074904382605163141518161494337

def pvk_to_wif2(key_hex: str) -> str:
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def make_entry(hdwallet: HDWallet, t: str) -> str:
	"""Build output block for a single private key hex string."""
	hdwallet.from_private_key(private_key=t)
	wif = pvk_to_wif2(t)
	return (
		f"{t}\n"
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

def process_line(line: str) -> Optional[str]:
	# FIX: create HDWallet instance per call so multiprocessing workers
	# each have their own instance and don't share/corrupt state.
	hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

	# FIX: use lists that accumulate entries across all loop iterations
	# instead of tuples that get overwritten (losing all but the last result).
	z1: List[str] = []
	z2: List[str] = []
	z3: List[str] = []
	z4: List[str] = []

	line = line.strip()
	if not line:
		return None

	try:
		i = int(line, 16)
	except ValueError:
		return None

	for x in range(i - 3, i + 4):
		if x < 1 or x > cur:
			continue
		x1 = int(x * math.pi)
		x2 = int(x / math.pi)
		y1 = int(x * math.e)
		y2 = int(x / math.e)

		for y in range(x1 - 3, x1 + 4):
			# FIX: also guard upper bound against secp256k1 curve order
			if y < 1 or y > cur:
				continue
			try:
				t = hex(y)[2:].zfill(64)
				z1.append(make_entry(hdwallet, t))
			except Exception:
				continue

		for y in range(x2 - 3, x2 + 4):
			if y < 1 or y > cur:
				continue
			try:
				t = hex(y)[2:].zfill(64)
				z2.append(make_entry(hdwallet, t))
			except Exception:
				continue

		for y in range(y1 - 3, y1 + 4):
			if y < 1 or y > cur:
				continue
			try:
				t = hex(y)[2:].zfill(64)
				z3.append(make_entry(hdwallet, t))
			except Exception:
				continue

		for y in range(y2 - 3, y2 + 4):
			if y < 1 or y > cur:
				continue
			try:
				t = hex(y)[2:].zfill(64)
				z4.append(make_entry(hdwallet, t))
			except Exception:
				continue

	combined = z1 + z2 + z3 + z4
	# FIX: return a single joined string (or None) so write_results
	# can simply call f.write(r) on each result item.
	return ''.join(combined) if combined else None

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
				chunk.append(b.decode('utf-8', errors='replace'))
			if not chunk:
				break
			yield chunk, f.tell()

def write_results(results: List[Optional[str]], out_path: Path, fsync: bool = True) -> None:
	# FIX: removed infinite while True / bare except retry loop that could
	# spin forever on a persistent error. Write once; raise on real failures.
	filtered = [r for r in results if r is not None]
	if not filtered:
		return
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with out_path.open('a', encoding='utf-8', buffering=1) as f:
		for r in filtered:
			f.write(r)
		f.flush()
		if fsync:
			os.fsync(f.fileno())

def main():
	parser = argparse.ArgumentParser(description="Stream input; progress by bytes read from input file position")
	parser.add_argument('-i', '--input',   type=str, default='input.txt',  help='input file path')
	parser.add_argument('-o', '--output',  type=str, default='output.txt', help='output file path')
	parser.add_argument('-w', '--workers', type=int, default=28,           help='number of processes (1 = no multiprocessing)')
	parser.add_argument('-c', '--chunk',   type=int, default=10000,        help='number of lines per chunk')
	parser.add_argument('--no-fsync', action='store_true',                 help='disable fsync() after each chunk to improve speed')
	args = parser.parse_args()

	in_path  = Path(args.input)
	out_path = Path(args.output)

	if not in_path.exists():
		print(f"Input file not found: {in_path}", file=sys.stderr)
		sys.exit(1)

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
			results = [process_line(line) for line in chunk]
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

	if last_pos < total_bytes:
		pbar.update(total_bytes - last_pos)

	pbar.close()
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
