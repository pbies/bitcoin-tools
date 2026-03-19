#!/usr/bin/env python3

import os
import base58
import sys
from multiprocessing import Pool, cpu_count
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD

KEY_HEX_LEN	= 64
NUM_WORKERS	= cpu_count() or 16
CHUNKSIZE	  = 128		  # items per imap batch


def read_hex_keys(filepath):
	"""
	Yield one 64-char hex private key per line from the input file.
	Lines shorter than 64 chars are skipped with a warning.
	Blank lines are skipped silently.
	"""
	with open(filepath, 'r') as f:
		for lineno, raw in enumerate(f, 1):
			line = raw.strip()
			if not line:
				continue  # skip blank lines without stopping
			if len(line) < KEY_HEX_LEN:
				print(f"[warn] line {lineno}: too short ({len(line)} chars), skipping",
					  file=sys.stderr)
				continue
			# If the line is exactly 64 chars, yield it directly.
			# If longer, slide a window and yield every 64-char substring.
			for start in range(len(line) - KEY_HEX_LEN + 1):
				yield line[start:start + KEY_HEX_LEN]


def pvk_to_wif_uncompressed(key_hex: str) -> str:
	"""Encode a raw private key as an uncompressed WIF (no 0x01 suffix)."""
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()


def pvk_to_wif_compressed(key_hex: str) -> str:
	"""Encode a raw private key as a compressed WIF (with 0x01 suffix)."""
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex) + b'\x01').decode()


def process_chunk(key_hex: str) -> str:
	"""
	Runs in a worker process.
	Returns a formatted result string on success, or an error tag string on failure.
	"""
	hw = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

	try:
		hw.from_private_key(private_key=key_hex)
	except Exception as e:
		return f"ERR:hd:{key_hex}:{e}"

	try:
		wif_uncompressed = pvk_to_wif_uncompressed(key_hex)
		wif_compressed   = pvk_to_wif_compressed(key_hex)
	except Exception as e:
		return f"ERR:wif:{key_hex}:{e}"

	result = (
		f"{key_hex}\n"
		f"{wif_uncompressed}\n"
		f"{wif_compressed}\n"
		#f"{hw.wif()}\n"
		f"{hw.address('P2PKH')}\n"
		f"{hw.address('P2SH')}\n"
		f"{hw.address('P2TR')}\n"
		f"{hw.address('P2WPKH')}\n"
		f"{hw.address('P2WPKH-In-P2SH')}\n"
		f"{hw.address('P2WSH')}\n"
		f"{hw.address('P2WSH-In-P2SH')}\n\n"
	)
	return result


if __name__ == "__main__":
	inp = "input.txt"
	out = "output.txt"

	total = hd_err = wif_err = written = 0

	with Pool(processes=NUM_WORKERS) as pool, open(out, 'w') as f:
		for v in pool.imap_unordered(
			process_chunk,
			read_hex_keys(inp),
			chunksize=CHUNKSIZE,
		):
			total += 1
			if v.startswith("ERR:hd:"):
				hd_err += 1
				print(v, file=sys.stderr)
			elif v.startswith("ERR:wif:"):
				wif_err += 1
				print(v, file=sys.stderr)
			elif v:
				f.write(v)
				written += 1

	print(
		f"\nDone. total={total}  written={written}  "
		f"hd_err={hd_err}  wif_err={wif_err}",
		file=sys.stderr,
	)
	print('\a', end='', file=sys.stderr)   # terminal bell
