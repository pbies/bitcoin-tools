#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, argparse
from itertools import islice
from multiprocessing import Pool
from Crypto.Hash import keccak
from ecpy.curves import Curve
from tqdm import tqdm

R_OFFSETS = [-1000, -100, -3, -2, -1, 0, 1, 2, 3, 100, 1000]
_cv = None

def _init_worker():
	global _cv
	_cv = Curve.get_curve('secp256k1')

def _eip55_checksum(addr_hex_no_0x: str) -> str:
	k = keccak.new(digest_bits=256)
	k.update(addr_hex_no_0x.encode('ascii'))
	hash_hex = k.hexdigest()
	out = []
	for ch, hh in zip(addr_hex_no_0x, hash_hex):
		out.append(ch.upper() if ch.isalpha() and int(hh, 16) >= 8 else ch)
	return '0x' + ''.join(out)

def _process_line(line_b: bytes) -> list[str]:
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
		addr_hex = k.hexdigest()[-40:]
		ck = _eip55_checksum(addr_hex)
		results.append(f'{hex(private_key)[2:].zfill(64)} {ck}\n')
	return results

def _worker_batch(lines: list[bytes]) -> tuple[list[str], int]:
	# Zwracamy (wyniki, liczba_przetworzonych_wejściowych_linii)
	out = []
	append = out.append
	for lb in lines:
		for row in _process_line(lb):
			append(row)
	return out, len(lines)

def _batched_iter(fh, batch_size: int):
	while True:
		batch = list(islice(fh, batch_size))
		if not batch:
			break
		returned = batch
		yield returned

def _fast_count_lines(path: str, bufsize: int = 1024 * 1024) -> int:
	# Szybkie liczenie linii bez dekodowania (po \n)
	count = 0
	with open(path, 'rb', buffering=bufsize) as f:
		while True:
			chunk = f.read(bufsize)
			if not chunk:
				break
			count += chunk.count(b'\n')
	# Jeżeli plik nie kończy się \n, a ostatnia linia niepusta — dolicz ją
	try:
		if count == 0:
			# mały plik: policz ruchem line-by-line
			with open(path, 'rb') as g:
				for _ in g:
					count += 1
			return count
		with open(path, 'rb') as g:
			g.seek(-1, os.SEEK_END)
			last = g.read(1)
		if last != b'\n':
			count += 1
	except OSError:
		pass
	return count

def parse_args():
	ap = argparse.ArgumentParser(description='ETH addr generator (skalowalny, batch + wiele procesów, lepszy progres)')
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

	if not os.path.exists(args.input):
		print(f'Brak pliku: {args.input}', file=sys.stderr)
		sys.exit(1)

	total_lines = _fast_count_lines(args.input)  # <<<< kluczowa zmiana
	if total_lines == 0:
		# nic do roboty
		open(args.output, 'wb').close()
		print('\a', end='', file=sys.stderr)
		return

	try:
		if os.path.exists(args.output):
			os.remove(args.output)
	except OSError:
		pass

	procs = max(1, args.procs)
	batch_size = max(1, args.batch)
	chunksize = max(1, args.chunksize)

	with open(args.input, 'rb', buffering=1024*1024) as fh, \
		Pool(processes=procs, initializer=_init_worker) as pool, \
		tqdm(total=total_lines, unit='line', smoothing=0.1, mininterval=0.3, desc='Processed') as pbar, \
		open(args.output, 'wb', buffering=1024*1024) as out:

		def batch_source():
			for batch in _batched_iter(fh, batch_size):
				yield batch

		for results, in_count in pool.imap_unordered(_worker_batch, batch_source(), chunksize=chunksize):
			# update progresu po ZAKOŃCZENIU pracy nad batchem
			pbar.update(in_count)
			if results:
				out.writelines(s.encode('ascii') for s in results)

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
