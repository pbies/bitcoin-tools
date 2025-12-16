#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from multiprocessing import Pool, cpu_count
from pathlib import Path
from tqdm import tqdm
from typing import Optional, Iterable, List
import argparse
import sys, os, base58, hashlib, base64

# Optional imports for platform-specific short critical-section locking
_IS_WIN = os.name == "nt"
if _IS_WIN:
	import msvcrt
else:
	import fcntl

# NOTE: user prefers tabs for indentation
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def _lock_file(f):
	# Acquire a short exclusive lock just for the write critical section
	if _IS_WIN:
		try:
			msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
		except OSError:
			msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
	else:
		fcntl.flock(f.fileno(), fcntl.LOCK_EX)

def _unlock_file(f):
	if _IS_WIN:
		try:
			msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
		except OSError:
			pass
	else:
		fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def process_line(line: str) -> Optional[str]:
	line = line.rstrip(b'\n')
	#try:
		#if hdwallet is None:
		#	return None
	sha = hashlib.sha256(line).digest()
	h=sha.hex()
	hdwallet.from_private_key(private_key=h)
	#except Exception:
	#	return None
	wif = pvk_to_wif2(h)
	a = (
		#f"{line}\n"
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
	return a.encode()

def read_lines(file_path: Path, chunk_size: int = 10000) -> Iterable[list]:
	with file_path.open('rb') as f:
		while True:
			chunk: List[bytes] = []
			for _ in range(chunk_size):
				l = f.readline()
				if not l:
					break
				chunk.append(l)
			if not chunk:
				break
			yield chunk

def write_results(results: Iterable[bytes], out_path: Path, fsync: bool = True) -> None:
	# Open -> short lock -> write -> flush -> optional fsync -> unlock -> close
	if not results:
		return
	out_path.parent.mkdir(parents=True, exist_ok=True)
	while True:
		try:
			with out_path.open('ab', buffering=0) as f:
				_lock_file(f)
				try:
					for r in results:
						if r is not None:
							f.write(r)
					if fsync:
						os.fsync(f.fileno())
				finally:
					_unlock_file(f)
					return
		except Exception:
			pass

def main():
	parser = argparse.ArgumentParser(description="Read lines -> process_line -> safe, momentary appends to output (progress by file position)")
	parser.add_argument('-i','--input', type=str, default='input.txt', help='input file path')
	parser.add_argument('-o','--output', type=str, default='output.txt', help='output file path')
	parser.add_argument('-w','--workers', type=int, default=24, help='number of processes (1 = no multiprocessing)')
	parser.add_argument('-c','--chunk', type=int, default=10000, help='number of lines per chunk')
	parser.add_argument('--no-fsync', action='store_true', help='disable fsync() after each chunk to improve speed')
	args = parser.parse_args()

	in_path = Path(args.input)
	out_path = Path(args.output)

	if not in_path.exists():
		sys.exit(1)

	# Truncate/create output file once and close immediately; no persistent handle kept open.
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with out_path.open('wb') as f:
		pass

	total_bytes = in_path.stat().st_size
	pbar = tqdm(total=total_bytes, unit='B', unit_scale=True, unit_divisor=1024, ncols=132)

	workers = max(1, args.workers)
	if workers > cpu_count():
		workers = cpu_count()

	if workers == 1:
		for chunk in read_lines(in_path, args.chunk):
			results = []
			for line in chunk:
				r = process_line(line)
				if r is not None:
					results.append(r)
			write_results(results, out_path, fsync=not args.no_fsync)
			pbar.update(sum(len(x) for x in chunk))
	else:
		with Pool(processes=workers) as pool:
			for chunk in read_lines(in_path, args.chunk):
				results = pool.map(process_line, chunk)
				write_results(results, out_path, fsync=not args.no_fsync)
				pbar.update(sum(len(x) for x in chunk))

	pbar.close()
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
