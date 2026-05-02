#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from pathlib import Path
from libcrypto import Wallet
import os, sys
from tqdm import tqdm
import traceback

CHUNK_LINES = 1000

def process_block(lines):
	out = []
	for line in lines:
		line = line.rstrip(b'\n').decode()
		try:
			wallet=Wallet(line)
		except Exception as e:
			# Zapisujemy błąd do stderr, ale kontynuujemy
			print(f"Error creating wallet from line: {e}", file=sys.stderr)
			continue
		try:
			p2pkh = wallet.get_address(coin="bitcoin", address_type="p2pkh")
			p2wsh = wallet.get_address(coin="bitcoin", address_type="p2sh-p2wpkh")
			p2wpkh = wallet.get_address(coin="bitcoin", address_type="p2wpkh")
			litecoin_address_p2pkh = wallet.get_address(coin="litecoin", address_type="p2pkh")
			litecoin_address_p2wsh = wallet.get_address(coin="litecoin", address_type="p2sh-p2wpkh")
			litecoin_address_p2wpkh = wallet.get_address(coin="litecoin", address_type="p2wpkh")
			out.append(
				line + "\n" +
				p2pkh + "\n" +
				p2wsh + "\n" +
				p2wpkh + "\n" +
				litecoin_address_p2pkh + "\n" +
				litecoin_address_p2wsh + "\n" +
				litecoin_address_p2wpkh + "\n" +
				"\n"
			)
		except Exception as e:
			print(f"Error getting addresses for {line}: {e}", file=sys.stderr)
			continue
	return ''.join(out)

def read_blocks(path):
	file_size = os.path.getsize(path)
	with open(path, 'rb', buffering=1024*1024) as f:
		with tqdm(total=file_size, unit='B', unit_scale=True, desc="Processing") as pbar:
			block = []
			for line in f:
				block.append(line)
				if len(block) >= CHUNK_LINES:
					yield block
					pbar.update(f.tell() - pbar.n)
					block = []
			if block:
				yield block
				pbar.update(file_size - pbar.n)

def main():
	inp = 'input.txt'
	out = 'output.txt'

	# Sprawdź czy plik wejściowy istnieje
	if not os.path.exists(inp):
		print(f"Input file {inp} not found!", file=sys.stderr)
		sys.exit(1)
	
	print(f"Input file size: {os.path.getsize(inp)} bytes", file=sys.stderr)
	
	# Wyczyść plik wyjściowy
	with open(out, 'w'):
		pass

	workers = cpu_count() - 1
	print(f"Using {workers} workers", file=sys.stderr)

	try:
		with Pool(workers) as p, open(out, 'a', buffering=1024*1024) as fo:
			for result in p.imap_unordered(process_block, read_blocks(inp), chunksize=100):
				if result:  # Tylko zapisuj jeśli coś zwrócono
					fo.write(result)
					fo.flush()  # Wymuś zapis do pliku
	except Exception as e:
		print(f"Critical error: {e}", file=sys.stderr)
		traceback.print_exc()
		sys.exit(1)

	print('\a', end='', file=sys.stderr)
	print("\nProcessing completed!", file=sys.stderr)

if __name__ == '__main__':
	main()
