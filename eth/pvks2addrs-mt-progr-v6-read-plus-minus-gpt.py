#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, argparse
from itertools import islice
from multiprocessing import Pool, get_start_method
from Crypto.Hash import keccak
from ecpy.curves import Curve
from tqdm import tqdm

# stałe
R_OFFSETS = [-1000, -100, -3, -2, -1, 0, 1, 2, 3, 100, 1000]

# zmienne per-proces (inicjalizowane w initializerze)
_cv = None

def _init_worker():
	"""
	Inicjalizacja zasobów per-proces (raz na proces).
	"""
	global _cv
	_cv = Curve.get_curve('secp256k1')

def _eip55_checksum(addr_hex_no_0x: str) -> str:
	"""
	Zwraca adres z EIP-55 checksum: '0x' + mieszane litery.
	Wejście: 40-znakowy hex bez prefiksu.
	"""
	k = keccak.new(digest_bits=256)
	k.update(addr_hex_no_0x.encode('ascii'))
	hash_hex = k.hexdigest()
	out = []
	for ch, hh in zip(addr_hex_no_0x, hash_hex):
		if ch.isalpha():
			# podnieś do wielkiej, jeśli odpowiadający hash nibble >= 8
			out.append(ch.upper() if int(hh, 16) >= 8 else ch.lower())
		else:
			out.append(ch)
	return '0x' + ''.join(out)

def _process_line(line_b: bytes) -> list[str]:
	"""
	Przetwarza jedną linię (bytes -> hex klucza), zwraca listę gotowych wierszy do outputu.
	Zwracamy listę, bo dla jednego wejścia generujemy wiele (offsety R_OFFSETS).
	"""
	line = line_b.decode('ascii', errors='ignore').strip()
	if not line:
		return []

	try:
		x = int(line, 16)
	except ValueError:
		return []

	results = []
	for off in R_OFFSETS:
		private_key = x + off
		if private_key <= 0:
			continue
		try:
			pu = private_key * _cv.generator
			concat_xy = pu.x.to_bytes(32, 'big') + pu.y.to_bytes(32, 'big')
		except Exception:
			continue

		k = keccak.new(digest_bits=256)
		k.update(concat_xy)
		addr_hex = k.hexdigest()[-40:]  # ostatnie 20 bajtów
		ck = _eip55_checksum(addr_hex)
		results.append(f'{hex(private_key)[2:].zfill(64)} {ck}\n')

	return results

def _worker_batch(lines: list[bytes]) -> list[str]:
	"""
	Worker na batch: dostaje listę linii bytes i zwraca złączoną listę wyników.
	"""
	out = []
	append = out.append
	for lb in lines:
		for row in _process_line(lb):
			append(row)
	return out

def _batched_iter(fh, batch_size: int):
	"""
	Czyta plik po batchach linii.
	"""
	while True:
		batch = list(islice(fh, batch_size))
		if not batch:
			break
		yield batch

def parse_args():
	ap = argparse.ArgumentParser(description='ETH addr generator (skalowalny, batch + wiele procesów)')
	ap.add_argument('-i', '--input', default='input.txt', help='plik wejściowy (domyślnie: input.txt)')
	ap.add_argument('-o', '--output', default='output.txt', help='plik wyjściowy (nadpisywany)')
	ap.add_argument('-p', '--procs', type=int, default=max(1, (os.cpu_count() or 1)),
		help='liczba procesów (domyślnie: liczba CPU)')
	ap.add_argument('-b', '--batch', type=int, default=5000,
		help='liczba linii na batch przekazywany do workera (domyślnie: 5000)')
	ap.add_argument('-c', '--chunksize', type=int, default=32,
		help='chunksize dla imap_unordered (domyślnie: 32)')
	return ap.parse_args()

def main():
	args = parse_args()

	# sanity / I/O
	if not os.path.exists(args.input):
		print(f'Brak pliku: {args.input}', file=sys.stderr)
		sys.exit(1)

	try:
		size_bytes = os.path.getsize(args.input)
	except OSError:
		size_bytes = 0

	# output reset
	try:
		if os.path.exists(args.output):
			os.remove(args.output)
	except OSError:
		pass

	# wskazówki dot. bardzo dużej liczby procesów
	# - na Linuksie zwykle warto pozostawić start_method='fork' (domyślny),
	#   na macOS/Windows i tak będzie 'spawn'.
	# - powyżej ~64 procesów zwiększ batch/chunksize, by ograniczyć IPC.
	procs = max(1, args.procs)
	batch_size = max(1, args.batch)
	chunksize = max(1, args.chunksize)

	# główny pipeline
	with open(args.input, 'rb', buffering=1024*1024) as fh, \
		Pool(processes=procs, initializer=_init_worker) as pool, \
		tqdm(total=size_bytes, unit='B', unit_scale=True, desc='Processing') as pbar, \
		open(args.output, 'wb', buffering=1024*1024) as out:

		# iterator batchy z pliku
		def batch_source():
			last_pos = fh.tell()
			for batch in _batched_iter(fh, batch_size):
				# raportuj progres na podstawie przyrostu pozycji pliku
				pos = fh.tell()
				pbar.update(max(0, pos - last_pos))
				last_pos = pos
				yield batch

		for results in pool.imap_unordered(_worker_batch, batch_source(), chunksize=chunksize):
			if results:
				out.writelines(s.encode('ascii') for s in results)

	# sygnał dźwiękowy po zakończeniu (jak w Twoim oryginale)
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
