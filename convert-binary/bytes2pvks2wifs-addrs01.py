#!/usr/bin/env python3

import os
import sys
import base58
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD

CHUNK_SIZE = 32

def read_binary_chunks(filepath, chunk_size=CHUNK_SIZE):
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

			yield pos, file_size, bytes(buf[:chunk_size])

			buf = buf[1:]
			pos += 1


def pvk_to_wif2(key_hex: str) -> str:
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()


if __name__ == "__main__":
	inp = "input.dat"
	out = "output.txt"

	hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

	total_chunks   = 0
	skipped_hd	 = 0
	skipped_wif	= 0
	written		= 0
	last_hd_error  = None
	last_wif_error = None

	PROGRESS_INTERVAL = 10 * 1024  # 10 KB
	last_progress_pos = -PROGRESS_INTERVAL

	with open(out, 'w') as o:
		for pos, file_size, chunk in read_binary_chunks(inp):
			total_chunks += 1

			if pos - last_progress_pos >= PROGRESS_INTERVAL:
				pct = pos / file_size * 100 if file_size else 0
				print(f"\r[{pos:,} / {file_size:,} bytes  {pct:.2f}%"
					  f"  written={written}  hd_err={skipped_hd}  wif_err={skipped_wif}]",
					  end='', flush=True)
				last_progress_pos = pos

			key_hex = chunk.hex()

			# --- step 1: load into hdwallet ---
			try:
				hdwallet.from_private_key(private_key=key_hex)
			except Exception as e:
				skipped_hd += 1
				last_hd_error = repr(e)
				continue

			# --- step 2: derive WIF via base58 ---
			try:
				wif = pvk_to_wif2(key_hex)
			except Exception as e:
				skipped_wif += 1
				last_wif_error = repr(e)
				continue

			# --- step 3: write ---
			a = (
				f"{key_hex}\n"
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
			o.write(a)
			written += 1

	print()  # newline after progress line
	print(f"\nSummary:")
	print(f"  Total chunks processed : {total_chunks:,}")
	print(f"  Written				: {written:,}")
	print(f"  Skipped (hdwallet err) : {skipped_hd:,}")
	print(f"  Skipped (wif err)	  : {skipped_wif:,}")
	if last_hd_error:
		print(f"  Last hdwallet error	: {last_hd_error}")
	if last_wif_error:
		print(f"  Last wif error		 : {last_wif_error}")
