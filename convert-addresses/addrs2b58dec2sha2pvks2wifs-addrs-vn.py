#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import hashlib
import os
import sys
import base58

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from multiprocessing import Pool, cpu_count
from pathlib import Path
from tqdm import tqdm
from typing import Optional, Iterable, List, Tuple

# ---------------------------------------------------------------------------
# Per-worker state: one HDWallet instance per process, not per line
# ---------------------------------------------------------------------------

_worker_hdwallet: Optional[HDWallet] = None


def _worker_init() -> None:
	"""Initializer for each worker process — create one HDWallet per process."""
	global _worker_hdwallet
	_worker_hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def sha256_hex(data: bytes) -> str:
	return hashlib.sha256(data).hexdigest()


def pvk_to_wif(key_hex: str) -> str:
	"""Convert a raw private-key hex string to uncompressed WIF."""
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()


def decode_and_hash(line: str) -> Optional[str]:
	"""
	Base58Check-decode *line*, SHA-256 hash the raw bytes,
	return the digest as a hex string — or None on decode failure.
	"""
	try:
		raw = base58.b58decode_check(line.rstrip('\n'))
	except Exception:
		return None
	return sha256_hex(raw)


def derive_addresses(pvk_hex: str, wallet: HDWallet) -> Optional[str]:
	"""
	Load *pvk_hex* into *wallet* and return a formatted multi-line block,
	or None if the key is invalid.
	"""
	try:
		wallet.from_private_key(private_key=pvk_hex)
	except Exception:
		return None

	wif_custom = pvk_to_wif(pvk_hex)
	return (
		f"{pvk_hex}\n"
		f"{wif_custom}\n"
		f"{wallet.wif()}\n"
		f"{wallet.address('P2PKH')}\n"
		f"{wallet.address('P2SH')}\n"
		f"{wallet.address('P2TR')}\n"
		f"{wallet.address('P2WPKH')}\n"
		f"{wallet.address('P2WPKH-In-P2SH')}\n"
		f"{wallet.address('P2WSH')}\n"
		f"{wallet.address('P2WSH-In-P2SH')}\n\n"
	)


# ---------------------------------------------------------------------------
# Top-level worker function (must be importable / picklable)
# ---------------------------------------------------------------------------

def process_line(line: str) -> Optional[str]:
	"""Decode → hash → derive addresses. Uses the per-process HDWallet."""
	pvk_hex = decode_and_hash(line)
	if pvk_hex is None:
		return None
	return derive_addresses(pvk_hex, _worker_hdwallet)


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def iter_chunks(file_path: Path, chunk_size: int) -> Iterable[Tuple[List[str], int]]:
	"""
	Yield (lines, byte_position) pairs.
	Reading in binary mode keeps tell() reliable on all platforms.
	"""
	with file_path.open('rb') as fh:
		while True:
			chunk: List[str] = []
			for _ in range(chunk_size):
				raw = fh.readline()
				if not raw:
					break
				chunk.append(raw.decode('utf-8', errors='replace'))
			if not chunk:
				break
			yield chunk, fh.tell()


def append_results(results: List[Optional[str]], out_path: Path, fsync: bool) -> None:
	"""Append non-None results to *out_path*, with optional fsync."""
	valid = [r for r in results if r is not None]
	if not valid:
		return
	try:
		with out_path.open('a', encoding='utf-8', buffering=1) as fh:
			fh.writelines(valid)
			fh.flush()
			if fsync:
				os.fsync(fh.fileno())
	except OSError as exc:
		# Don't silently swallow disk/permission errors
		print(f"[ERROR] Could not write to {out_path}: {exc}", file=sys.stderr)
		sys.exit(1)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
	parser = argparse.ArgumentParser(
		description="Derive Bitcoin addresses from Base58Check-encoded input lines."
	)
	parser.add_argument('-i', '--input',   default='input.txt',  help='input file path')
	parser.add_argument('-o', '--output',  default='output.txt', help='output file path')
	parser.add_argument(
		'-w', '--workers', type=int, default=0,
		help='worker processes (0 = cpu_count - 2, 1 = single-process)'
	)
	parser.add_argument('-c', '--chunk', type=int, default=10_000, help='lines per chunk')
	parser.add_argument('--fsync', action='store_true',
						help='fsync after every chunk (safe but slower)')
	args = parser.parse_args()

	in_path  = Path(args.input)
	out_path = Path(args.output)

	if not in_path.exists():
		print(f"[ERROR] Input file not found: {in_path}", file=sys.stderr)
		sys.exit(1)

	# Determine worker count — never less than 1, never more than cpu_count-2
	avail   = max(1, cpu_count() - 2)
	workers = avail if args.workers <= 0 else min(args.workers, avail)

	# Truncate / create the output file once upfront
	out_path.parent.mkdir(parents=True, exist_ok=True)
	out_path.write_text('', encoding='utf-8')

	total_bytes = in_path.stat().st_size
	pbar = tqdm(
		total=total_bytes,
		unit='B', unit_scale=True, unit_divisor=1024,
		ncols=132,
	)

	last_pos = 0

	def _advance(pos: int) -> None:
		nonlocal last_pos
		delta = pos - last_pos
		if delta > 0:
			pbar.update(delta)
		last_pos = pos

	if workers == 1:
		# Single-process path: create one wallet inline
		wallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
		for chunk, pos in iter_chunks(in_path, args.chunk):
			results = []
			for line in chunk:
				pvk_hex = decode_and_hash(line)
				if pvk_hex is not None:
					r = derive_addresses(pvk_hex, wallet)
					if r is not None:
						results.append(r)
			append_results(results, out_path, fsync=args.fsync)
			_advance(pos)
	else:
		# Multi-process path: each worker owns its HDWallet via initializer
		with Pool(processes=workers, initializer=_worker_init) as pool:
			for chunk, pos in iter_chunks(in_path, args.chunk):
				# imap_unordered keeps the pipeline flowing without waiting
				# for the slowest item before starting the next batch
				results = list(pool.imap_unordered(process_line, chunk, chunksize=256))
				append_results(results, out_path, fsync=args.fsync)
				_advance(pos)

	# Close progress bar to 100% if OS reported unusual tell() values
	if last_pos < total_bytes:
		pbar.update(total_bytes - last_pos)
	pbar.close()

	# Terminal bell to signal completion
	print('\a', end='', file=sys.stderr)


if __name__ == '__main__':
	main()
