#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import os, base58, sys, hashlib
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD

# Larger chunks = better multiprocessing efficiency
CHUNK_LINES = 2000

# Process-local HDWallet instance
_process_hdwallet1 = None
_process_hdwallet2 = None
_process_hdwallet3 = None

def init_worker():
	"""Initialize HDWallet once per worker process"""
	global _process_hdwallet1
	global _process_hdwallet2
	global _process_hdwallet3
	_process_hdwallet1 = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	_process_hdwallet2 = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	_process_hdwallet3 = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def pvk_to_wif2(key_hex):
	"""Fast WIF conversion"""
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def reverse_by_bytes(hex_str):
	hex_str = hex_str.replace(" ", "").lower()
	if len(hex_str) % 2 != 0:
		raise ValueError("Hex string must have even length")
	bytes_list = [hex_str[i:i+2] for i in range(0, len(hex_str), 2)]
	return "".join(bytes_list[::-1])

def process_block(lines):
	"""Process a block of lines with optimized string building.
	Returns (result_str, byte_count) so the caller can update the progress bar
	without needing to keep a reference to the original block."""
	hdwallet1 = _process_hdwallet1
	hdwallet2 = _process_hdwallet2
	hdwallet3 = _process_hdwallet3
	output_parts = []
	byte_count = 0

	for line in lines:
		byte_count += len(line)
		line = line.rstrip(b'\n')[::-1]
		s=hashlib.sha256(line).hexdigest()
		t=reverse_by_bytes(s)
		u=s[::-1]

		try:
			hdwallet1.from_private_key(private_key=s)
			hdwallet2.from_private_key(private_key=t)
			hdwallet3.from_private_key(private_key=u)
		except:
			continue

		wif_manual    = pvk_to_wif2(s)
		wif_hdwallet  = hdwallet1.wif()
		p2pkh         = hdwallet1.address('P2PKH')
		p2sh          = hdwallet1.address('P2SH')
		p2tr          = hdwallet1.address('P2TR')
		p2wpkh        = hdwallet1.address('P2WPKH')
		p2wpkh_p2sh   = hdwallet1.address('P2WPKH-In-P2SH')
		p2wsh         = hdwallet1.address('P2WSH')
		p2wsh_p2sh    = hdwallet1.address('P2WSH-In-P2SH')

		output_parts.append(
			f"{line.decode('utf-8', errors='ignore')}\n"
			f"{wif_manual}\n"
			f"{wif_hdwallet}\n"
			f"{p2pkh}\n"
			f"{p2sh}\n"
			f"{p2tr}\n"
			f"{p2wpkh}\n"
			f"{p2wpkh_p2sh}\n"
			f"{p2wsh}\n"
			f"{p2wsh_p2sh}\n\n"
		)

		wif_manual    = pvk_to_wif2(t)
		wif_hdwallet  = hdwallet2.wif()
		p2pkh         = hdwallet2.address('P2PKH')
		p2sh          = hdwallet2.address('P2SH')
		p2tr          = hdwallet2.address('P2TR')
		p2wpkh        = hdwallet2.address('P2WPKH')
		p2wpkh_p2sh   = hdwallet2.address('P2WPKH-In-P2SH')
		p2wsh         = hdwallet2.address('P2WSH')
		p2wsh_p2sh    = hdwallet2.address('P2WSH-In-P2SH')

		output_parts.append(
			f"{line.decode('utf-8', errors='ignore')}\n"
			f"{wif_manual}\n"
			f"{wif_hdwallet}\n"
			f"{p2pkh}\n"
			f"{p2sh}\n"
			f"{p2tr}\n"
			f"{p2wpkh}\n"
			f"{p2wpkh_p2sh}\n"
			f"{p2wsh}\n"
			f"{p2wsh_p2sh}\n\n"
		)

		wif_manual    = pvk_to_wif2(u)
		wif_hdwallet  = hdwallet3.wif()
		p2pkh         = hdwallet3.address('P2PKH')
		p2sh          = hdwallet3.address('P2SH')
		p2tr          = hdwallet3.address('P2TR')
		p2wpkh        = hdwallet3.address('P2WPKH')
		p2wpkh_p2sh   = hdwallet3.address('P2WPKH-In-P2SH')
		p2wsh         = hdwallet3.address('P2WSH')
		p2wsh_p2sh    = hdwallet3.address('P2WSH-In-P2SH')

		output_parts.append(
			f"{line.decode('utf-8', errors='ignore')}\n"
			f"{wif_manual}\n"
			f"{wif_hdwallet}\n"
			f"{p2pkh}\n"
			f"{p2sh}\n"
			f"{p2tr}\n"
			f"{p2wpkh}\n"
			f"{p2wpkh_p2sh}\n"
			f"{p2wsh}\n"
			f"{p2wsh_p2sh}\n\n"
		)

	return ''.join(output_parts), byte_count

def read_blocks(path, chunk_size=CHUNK_LINES):
	"""Lazily yield blocks of lines from the file — never loads the whole file."""
	with open(path, 'rb', buffering=8*1024*1024) as f:
		block = []
		for line in f:
			block.append(line)
			if len(block) >= chunk_size:
				yield block
				block = []
		if block:
			yield block

def main():
	inp = 'input.txt'
	out = 'output.txt'

	if not os.path.exists(inp):
		print(f"Error: {inp} not found!", file=sys.stderr)
		return

	total_bytes = os.path.getsize(inp)

	# Clear output file
	open(out, 'w').close()

	workers = max(1, cpu_count() - 2)
	print(f"Using {workers} worker processes", file=sys.stderr)

	with Pool(workers, initializer=init_worker) as p, \
		 open(out, 'a', buffering=8*1024*1024) as fo, \
		 tqdm(total=total_bytes, unit='B', unit_scale=True, desc="Processing") as bar:

		# imap_unordered consumes the generator lazily: each block is read
		# from disk only as a worker becomes free, so memory stays bounded.
		for result_str, byte_count in p.imap_unordered(
			process_block,
			read_blocks(inp),
			chunksize=1,
		):
			fo.write(result_str)
			bar.update(byte_count)

	print('\nDone!', file=sys.stderr)
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
