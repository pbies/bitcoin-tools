#!/usr/bin/env python3

import os
import base58
from multiprocessing import Pool, cpu_count
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD

CHUNK_SIZE	 = 32
NUM_WORKERS	= cpu_count() or 4
CHUNKSIZE	  = 128		  # items per imap batch
PROGRESS_EVERY = 10 * 1024   # print progress every 10 KB


def read_binary_chunks(filepath, chunk_size=CHUNK_SIZE):
	"""Yield (pos, file_size, key_hex) sliding one byte at a time, streaming."""
	file_size = os.path.getsize(filepath)
	buf = bytearray()
	with open(filepath, 'rb') as f:
		pos = 0
		while True:
			needed = chunk_size - len(buf)
			if needed > 0:
				data = f.read(needed)
				if not data:
					break
				buf.extend(data)
			if len(buf) < chunk_size:
				break
			yield pos, file_size, buf[:chunk_size].hex()
			buf = buf[1:]
			pos += 1


def pvk_to_wif2(key_hex: str) -> str:
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()


def process_chunk(args):
	"""
	Runs in a worker process.
	Returns (result_str, err_tag) where err_tag is None on success.
	"""
	pos, file_size, key_hex = args
	hw = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

	try:
		hw.from_private_key(private_key=key_hex)
	except Exception:
		return pos, file_size, None, "hd"

	try:
		wif = pvk_to_wif2(key_hex)
	except Exception:
		return pos, file_size, None, "wif"

	result = (
		f"{key_hex}\n"
		f"{wif}\n"
		f"{hw.wif()}\n"
		f"{hw.address('P2PKH')}\n"
		f"{hw.address('P2SH')}\n"
		f"{hw.address('P2TR')}\n"
		f"{hw.address('P2WPKH')}\n"
		f"{hw.address('P2WPKH-In-P2SH')}\n"
		f"{hw.address('P2WSH')}\n"
		f"{hw.address('P2WSH-In-P2SH')}\n\n"
	)
	return pos, file_size, result, None


if __name__ == "__main__":
	inp = "input.dat"
	out = "output.txt"

	total = hd_err = wif_err = written = 0
	last_progress_pos = -PROGRESS_EVERY

	with Pool(processes=NUM_WORKERS) as pool, open(out, 'w') as f:
		for pos, file_size, result, err in pool.imap_unordered(
			process_chunk,
			read_binary_chunks(inp),
			chunksize=CHUNKSIZE,
		):
			total += 1
			if err == "hd":
				hd_err += 1
			elif err == "wif":
				wif_err += 1
			elif result:
				f.write(result)
				written += 1

			if pos - last_progress_pos >= PROGRESS_EVERY:
				pct = pos / file_size * 100 if file_size else 0
				print(
					f"\r[{pos:,} / {file_size:,} bytes  {pct:.2f}%"
					f"  written={written}  hd_err={hd_err}  wif_err={wif_err}]",
					end='', flush=True,
				)
				last_progress_pos = pos

	print()
	print(f"\nSummary:")
	print(f"  Workers				: {NUM_WORKERS}")
	print(f"  Total chunks processed : {total:,}")
	print(f"  Written				: {written:,}")
	print(f"  Skipped (hdwallet err) : {hd_err:,}")
	print(f"  Skipped (wif err)	  : {wif_err:,}")
