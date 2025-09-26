#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, argparse, multiprocessing as mp
from itertools import islice
from Crypto.Hash import keccak
from ecpy.curves import Curve
from tqdm import tqdm

R_OFFSETS = [-1000, -100, -3, -2, -1, 0, 1, 2, 3, 100, 1000]

# globalne w workerze
_cv = None
_q = None
_subbatch = None

def _init_worker(q, subbatch: int):
	"""
	Inicjalizacja per-proces: krzywa + uchwyt do kolejki + rozmiar sub-batcha.
	"""
	global _cv, _q, _subbatch
	_cv = Curve.get_curve('secp256k1')
	_q = q
	_subbatch = max(1, int(subbatch))

def _eip55_checksum(addr_hex_no_0x: str) -> str:
	k = keccak.new(digest_bits=256)
	k.update(addr_hex_no_0x.encode('ascii'))
	h = k.hexdigest()
	out = []
	for ch, hh in zip(addr_hex_no_0x, h):
		out.append(ch.upper() if ch.isalpha() and int(hh, 16) >= 8 else ch)
	return '0x' + ''.join(out)

def _process_one(line_b: bytes) -> list[str]:
	line = line_b.decode('ascii', errors='ignore').strip()
	if not line:
		return []
	try:
		x = int(line, 16)
	except ValueError:
		return []
	results = []
	for off in R_OFFSETS:
		pk = x + off
		if pk <= 0:
			continue
		try:
			pu = pk * _cv.generator
			concat_xy = pu.x.to_bytes(32, 'big') + pu.y.to_bytes(32, 'big')
		except Exception:
			continue
		k = keccak.new(digest_bits=256)
		k.update(concat_xy)
		addr_hex = k.hexdigest()[-40:]
		ck = _eip55_checksum(addr_hex)
		results.append(f'{hex(pk)[2:].zfill(64)} {ck}\n')
	return results

def _worker(lines: list[bytes]) -> int:
	"""
	Pracuje na batchu, ale co _subbatch linii wysyła częściowe wyniki do kolejki.
	Zwraca łączną liczbę linii wejściowych (dla statystyki).
	"""
	buf = []
	buf_append = buf.append
	emitted = 0
	count_in = 0

	for i, lb in enumerate(lines, 1):
		count_in += 1
		for row in _process_one(lb):
			buf_append(row)
		if (i % _subbatch) == 0:
			if buf:
				# pakujemy do jednego bytes, mniej IPC
				_q.put((b''.join(s.encode('ascii') for s in buf), _subbatch))
				emitted += _subbatch
				buf = []
				buf_append = buf.append

	# resztka
	rem = count_in - emitted
	if buf:
		_q.put((b''.join(s.encode('ascii') for s in buf), rem))
	elif rem:
		# nic do zapisania, ale zaktualizuj progres o rem
		_q.put((b'', rem))

	return count_in

def _batched_iter(fh, batch_size: int):
	while True:
		batch = list(islice(fh, batch_size))
		if not batch:
			break
		yield batch

def _fast_count_lines(path: str, bufsize: int = 1024 * 1024) -> int:
	cnt = 0
	with open(path, 'rb', buffering=bufsize) as f:
		while True:
			chunk = f.read(bufsize)
			if not chunk:
				break
			cnt += chunk.count(b'\n')
	try:
		if cnt == 0:
			with open(path, 'rb') as g:
				for _ in g:
					cnt += 1
			return cnt
		with open(path, 'rb') as g:
			g.seek(-1, os.SEEK_END)
			if g.read(1) != b'\n':
				cnt += 1
	except OSError:
		pass
	return cnt

def parse_args():
	ap = argparse.ArgumentParser(description='ETH addr generator: multiprocessing + live zapis + płynny progres')
	ap.add_argument('-i', '--input', default='input.txt', help='plik wejściowy')
	ap.add_argument('-o', '--output', default='output.txt', help='plik wyjściowy (dopisywany)')
	ap.add_argument('-p', '--procs', type=int, default=max(1, (os.cpu_count() or 1)),
		help='liczba procesów')
	ap.add_argument('-b', '--batch', type=int, default=5000,
		help='rozmiar batcha przekazywanego do workera')
	ap.add_argument('-s', '--subbatch', type=int, default=200,
		help='rozmiar sub-batcha wysyłanego przez workera (częstotliwość zapisu/progresu)')
	ap.add_argument('-c', '--queue-cap', type=int, default=1024,
		help='maksymalny rozmiar kolejki (kontrola pamięci)')
	ap.add_argument('--fsync', action='store_true',
		help='po każdym zapisie wykonaj fsync (wolniej, ale bezpieczniej)')
	return ap.parse_args()

def main():
	args = parse_args()

	if not os.path.exists(args.input):
		print(f'Brak pliku: {args.input}', file=sys.stderr)
		sys.exit(1)

	total_lines = _fast_count_lines(args.input)
	if total_lines == 0:
		open(args.output, 'wb').close()
		print('\a', end='', file=sys.stderr)
		return

	# przygotuj plik wyjściowy (nadpisujemy)
	try:
		if os.path.exists(args.output):
			os.remove(args.output)
	except OSError:
		pass

	procs = max(1, args.procs)
	batch_size = max(1, args.batch)
	subbatch = max(1, args.subbatch)

	# Kolejka z pojemnością (żeby nie zalać RAM przy bardzo szybkim CPU)
	q = mp.Queue(maxsize=max(1, args.queue_cap))

	pool = mp.Pool(processes=procs, initializer=_init_worker, initargs=(q, subbatch))

	# Harmonogram: wysyłamy zadania apply_async, jednocześnie w pętli opróżniamy kolejkę do pliku i aktualizujemy progres.
	pending = []
	written_lines = 0

	with open(args.input, 'rb', buffering=1024*1024) as fh, \
		open(args.output, 'ab', buffering=1024*1024) as out, \
		tqdm(total=total_lines, unit='line', smoothing=0.05, mininterval=0.1, desc='Processed') as pbar:

		# wysyłaj batch'e dopóki są dane
		for batch in _batched_iter(fh, batch_size):
			pending.append(pool.apply_async(_worker, (batch,)))
			# po każdym wysłaniu próbujemy spuścić kolejkę (non-blocking)
			while True:
				try:
					chunk, inc = q.get_nowait()
				except Exception:
					break
				if chunk:
					out.write(chunk)
				if args.fsync:
					out.flush(); os.fsync(out.fileno())
				else:
					out.flush()
				written_lines += inc
				pbar.update(inc)

		# wszystkie zadania wysłane — teraz czekamy aż zakończą, w tle opróżniając kolejkę
		for r in pending:
			while True:
				if r.ready():
					# ostatnie porcje mogły jeszcze zostać w kolejce — spróbuj je zebrać
					try:
						chunk, inc = q.get_nowait()
						if chunk:
							out.write(chunk)
						if args.fsync:
							out.flush(); os.fsync(out.fileno())
						else:
							out.flush()
						written_lines += inc
						pbar.update(inc)
						continue
					except Exception:
						pass
					# odbierz wynik (dla ewentualnej diagnostyki)
					try:
						_ = r.get(timeout=0.1)
					except Exception as e:
						print(f'Worker error: {e}', file=sys.stderr)
					break
				else:
					# w międzyczasie konsumuj kolejkę z krótkim czekaniem
					try:
						chunk, inc = q.get(timeout=0.1)
						if chunk:
							out.write(chunk)
						if args.fsync:
							out.flush(); os.fsync(out.fileno())
						else:
							out.flush()
						written_lines += inc
						pbar.update(inc)
					except Exception:
						pass

		# Opróżnij kolejkę do końca (jeśli coś jeszcze zostało)
		while True:
			try:
				chunk, inc = q.get_nowait()
			except Exception:
				break
			if chunk:
				out.write(chunk)
			if args.fsync:
				out.flush(); os.fsync(out.fileno())
			else:
				out.flush()
			written_lines += inc
			pbar.update(inc)

	# porządek
	pool.close()
	pool.join()

	# dzwonek
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
