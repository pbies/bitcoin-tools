#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from multiprocessing import Pool, cpu_count
from pathlib import Path
from tqdm import tqdm
from typing import Optional, Iterable, List
import argparse
import sys, os, base58, time
import signal

_IS_WIN = os.name == "nt"
if _IS_WIN:
	import msvcrt
else:
	import fcntl

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Dogecoin as Doge
from hdwallet.cryptocurrencies import Litecoin as Lite
from hdwallet.hds import BIP32HD


def pvk_to_wif2(key_hex: str, coin: str) -> str:
	# Doge: 0x9e, LTC (uncompressed legacy): 0xb0
	if coin == 'Lite':
		return base58.b58encode_check(b'\xb0' + bytes.fromhex(key_hex)).decode()
	elif coin == 'Doge':
		return base58.b58encode_check(b'\x9e' + bytes.fromhex(key_hex)).decode()
	else:
		return ""


def _lock_file(f):
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


def process_line(n: int) -> Optional[str]:
	# Format int -> 64-char hex
	pvk_hex = f"{int(n):064x}"
	out = []

	for crypto, tag in ((Doge, 'Doge'), (Lite, 'Lite')):
		try:
			hdw = HDWallet(cryptocurrency=crypto, hd=BIP32HD)
			hdw.from_private_key(private_key=pvk_hex)
			wif_custom = pvk_to_wif2(pvk_hex, tag)
			wif_lib = ""
			try:
				wif_lib = hdw.wif()
			except Exception:
				wif_lib = ""

			out.append(f"{pvk_hex}\n{wif_custom}\n{wif_lib}\n")

			# Try a conservative set first; altcoins may not support all types
			addr_types = [
				'P2PKH',
				'P2SH',
				'P2WPKH',
				'P2WPKH-In-P2SH',
				'P2TR',
				'P2WSH',
				'P2WSH-In-P2SH',
			]
			for t in addr_types:
				try:
					a = hdw.address(t)
					if a:
						out.append(f"{a}\n")
				except Exception:
					continue
			out.append("\n")
		except Exception:
			continue

	if not out:
		return None
	return ''.join(out)


def iter_range(start: int, end: int) -> Iterable[int]:
	# Inclusive range
	i = start
	while i <= end:
		yield i
		i += 1


def write_results(results: Iterable[str], out_path: Path, fsync: bool) -> None:
	buf = [r for r in results if r]
	if not buf:
		return
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with out_path.open('a', encoding='utf-8', buffering=1) as f:
		_lock_file(f)
		try:
			for r in buf:
				f.write(r)
			f.flush()
			if fsync:
				os.fsync(f.fileno())
		finally:
			_unlock_file(f)


def main():
	parser = argparse.ArgumentParser(
		description="Convert private keys to WIF and addresses for Dogecoin/Litecoin."
	)
	parser.add_argument('-o', '--output', default='output.txt', help='output file path')
	parser.add_argument('-w', '--workers', type=int, default=max(1, cpu_count() - 1), help='number of processes')
	parser.add_argument('-s', '--start', type=int, default=1, help='start of keyspace (inclusive)')
	parser.add_argument('-e', '--end', type=int, default=5_000_000_000, help='end of keyspace (inclusive)')
	parser.add_argument('-b', '--buffer', type=int, default=2000, help='write buffer size (lines)')
	parser.add_argument('--mproc-chunksize', type=int, default=500, help='multiprocessing chunk size')
	parser.add_argument('--fsync', action='store_true', help='fsync() after each buffered write (slow)')

	args = parser.parse_args()

	start = int(args.start)
	end = int(args.end)
	if end < start:
		end = start

	out_path = Path(args.output)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	# Truncate output file at start
	with out_path.open('w', encoding='utf-8'):
		pass

	total = end - start + 1
	pbar = tqdm(total=total, unit='keys', ncols=132)

	# SIGINT handling to close pool cleanly
	original_sigint = signal.getsignal(signal.SIGINT)

	def _init_worker():
		signal.signal(signal.SIGINT, signal.SIG_IGN)

	results_buffer: List[str] = []

	try:
		workers = max(1, min(args.workers, cpu_count()))
		if workers == 1:
			for i, n in enumerate(iter_range(start, end), 1):
				res = process_line(n)
				if res:
					results_buffer.append(res)
				if len(results_buffer) >= args.buffer:
					write_results(results_buffer, out_path, fsync=args.fsync)
					results_buffer.clear()
				if (i % 1024) == 0:
					pbar.update(1024)
			# tail
			if results_buffer:
				write_results(results_buffer, out_path, fsync=args.fsync)
				results_buffer.clear()
			remaining = total % 1024
			if remaining:
				pbar.update(remaining)
		else:
			signal.signal(signal.SIGINT, original_sigint)
			with Pool(processes=workers, initializer=_init_worker) as pool:
				im = pool.imap_unordered(process_line, iter_range(start, end), chunksize=args.mproc_chunksize)
				count = 0
				for res in im:
					count += 1
					if res:
						results_buffer.append(res)
					if len(results_buffer) >= args.buffer:
						write_results(results_buffer, out_path, fsync=args.fsync)
						results_buffer.clear()
					if (count % 2048) == 0:
						pbar.update(2048)
				# drain
				if results_buffer:
					write_results(results_buffer, out_path, fsync=args.fsync)
					results_buffer.clear()
				remaining = total % 2048
				if remaining:
					pbar.update(remaining)

	finally:
		pbar.close()
		# Audible bell to signal end
		print('\a', end='', file=sys.stderr)


if __name__ == '__main__':
	main()
