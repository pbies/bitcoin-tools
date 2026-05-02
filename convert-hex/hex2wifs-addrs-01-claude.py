#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP84HD
from hdwallet.mnemonics import BIP39Mnemonic
from hdwallet.seeds import BIP39Seed
from hdwallet.entropies import BIP39Entropy
from multiprocessing import Pool
from tqdm import tqdm
import base58
import sys
import os

OUTPUT_FILE = 'output.txt'
CHUNK_SIZE = 100		# lines per worker task
WRITE_BATCH = 50		# results buffered before flushing to disk
MAX_INT = 2 ** 128


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pvk_to_wif(key_hex: str) -> str:
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()


def get_addresses(wallet):
	return (
		wallet.address('P2PKH'),
		wallet.address('P2SH'),
		wallet.address('P2TR'),
		wallet.address('P2WPKH'),
		wallet.address('P2WPKH-In-P2SH'),
		wallet.address('P2WSH'),
		wallet.address('P2WSH-In-P2SH'),
	)


# ---------------------------------------------------------------------------
# Per-line worker (runs in child process)
# ---------------------------------------------------------------------------

def build_wallets(key: str):
	"""
	Returns a list of result strings for *key*, or an empty list on any error.
	All exceptions are swallowed so a bad line never kills the worker.
	"""
	key = key.strip()
	if not key:
		return []

	try:
		i   = int(key, 16) % MAX_INT
		s1  = hex(i)[2:].zfill(128)   # seed	   (64 bytes → 128 hex chars)
		s2  = hex(i)[2:].zfill(64)	# private key (32 bytes → 64 hex chars)
		s3  = hex(i)[2:].zfill(32)	# entropy	(16 bytes → 32 hex chars)
		s4  = hex(i)[2:].zfill(128)   # xprv seed  (same length as s1)
	except Exception:
		return []

	# Build the four wallet variants; keep going even if one fails
	wallet_candidates = []
	for factory in (
		lambda: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_seed(BIP39Seed(s1)),
		lambda: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_private_key(s2),
		lambda: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_entropy(BIP39Entropy(s3)),
		lambda: HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_xprivate_key(s4),   # BUG FIX: was DWallet
	):
		try:
			wallet_candidates.append(factory())
		except Exception:
			wallet_candidates.append(None)

	results = []
	for w in wallet_candidates:
		if w is None:
			continue
		try:
			pvk_hex = w.private_key()
			if not pvk_hex:
				continue
			wif = pvk_to_wif(pvk_hex)
			p2pkh, p2sh, p2tr, p2wpkh, p2wpkh_p2sh, p2wsh, p2wsh_p2sh = get_addresses(w)
			results.append(
				f"{key}\n{wif}\n{w.wif()}\n"		  # BUG FIX: was `wallet.wif()`
				f"{p2pkh}\n{p2sh}\n{p2tr}\n{p2wpkh}\n"
				f"{p2wpkh_p2sh}\n{p2wsh}\n{p2wsh_p2sh}\n\n"
			)
		except Exception:
			continue

	return results


# ---------------------------------------------------------------------------
# Streaming input helpers
# ---------------------------------------------------------------------------

def count_lines(path: str) -> int:
	"""Fast newline count — one pass, no full file in RAM."""
	count = 0
	with open(path, 'rb') as f:
		for chunk in iter(lambda: f.read(1 << 20), b''):
			count += chunk.count(b'\n')
	return count


def line_generator(path: str):
	"""Yield non-empty stripped lines one at a time."""
	with open(path, encoding='utf-8', errors='replace') as f:
		for line in f:
			line = line.strip()
			if line:
				yield line


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
	input_file = 'input.txt'
	if not os.path.exists(input_file):
		print("Error: input.txt not found.", file=sys.stderr)
		sys.exit(1)

	# Count lines first (single fast pass) so tqdm can show a real ETA
	print("Counting input lines…", end=' ', flush=True, file=sys.stderr)
	total = count_lines(input_file)
	print(f"{total:,}", file=sys.stderr)

	if total == 0:
		print("No input lines to process.", file=sys.stderr)
		sys.exit(0)

	# Truncate / create output file
	open(OUTPUT_FILE, 'w').close()

	num_workers = min(16, os.cpu_count() or 4)

	write_buffer = []

	def flush_buffer(buf, outfile):
		for block in buf:
			outfile.writelines(block)
		buf.clear()

	with (
		open(OUTPUT_FILE, 'a', buffering=1 << 16) as outfile,
		Pool(processes=num_workers) as pool,
		tqdm(total=total, desc="Processing", unit="key", dynamic_ncols=True) as pbar,
	):
		for result_list in pool.imap_unordered(
			build_wallets,
			line_generator(input_file),
			chunksize=CHUNK_SIZE,
		):
			pbar.update(1)
			if result_list:
				write_buffer.append(result_list)
				if len(write_buffer) >= WRITE_BATCH:
					flush_buffer(write_buffer, outfile)

		# Flush remainder
		flush_buffer(write_buffer, outfile)

	print('\a', end='', file=sys.stderr)   # terminal bell
	print(f"Done. Results saved to {OUTPUT_FILE}")


if __name__ == '__main__':
	main()
