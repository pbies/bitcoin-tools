#!/usr/bin/env python3

import os
import sys
from itertools import islice
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

# Keccak-256 (ETH, nie NIST SHA3)
from Crypto.Hash import keccak

# Optional: szybkie libsecp256k1 przez coincurve (jeśli dostępne)
_HAS_COINCURVE = False
try:
	import coincurve
	_HAS_COINCURVE = True
except Exception:
	pass

# Fallback: ECPy (wolniejsze, czysty Python)
if not _HAS_COINCURVE:
	from ecpy.curves import Curve
	_CV = None
	_G = None

# --- parametry ---
INFILE = 'input.txt'
OUTFILE = 'output.txt'
PROCESSES = min(4, cpu_count())
BATCH_LINES = 20000			# liczba linii na partię do procesu
TQDM_STEP_BYTES = 100_000	# co ile bajtów aktualizować pasek

# --- init worker ---
def _init_worker():
	global _CV, _G
	if not _HAS_COINCURVE:
		_CV = Curve.get_curve('secp256k1')
		_G = _CV.generator

# --- EIP-55 checksum bez Web3 ---
def _to_checksum_address(hex40_lower):
	# hex40_lower: 40 znaków lower-case bez '0x'
	k = keccak.new(digest_bits=256)
	k.update(hex40_lower.encode('ascii'))
	digest = k.hexdigest()
	out = []
	for i, ch in enumerate(hex40_lower):
		if ch.isalpha():
			# jeżeli odpowiedni nibble >= 8 -> wielka litera
			if int(digest[i], 16) >= 8:
				out.append(ch.upper())
			else:
				out.append(ch)
		else:
			out.append(ch)
	return '0x' + ''.join(out)

# --- rdzeń: z klucza prywatnego (hex) -> ETH checksum address ---
def _privhex_to_eth(line_hex):
	# line_hex: str, bez \n, może mieć spacje; oczekujemy czystego hex
	try:
		priv_int = int(line_hex, 16)
		if priv_int <= 0:
			return None
	except Exception:
		return None

	try:
		if _HAS_COINCURVE:
			# priv -> pub (uncompressed 65B: 0x04 || X || Y)
			priv = coincurve.PrivateKey.from_int(priv_int)
			pub_uncomp = priv.public_key.format(False)	# 65B
			xy = pub_uncomp[1:]						# 64B X||Y
		else:
			# ECPy: punkt = k*G
			P = priv_int * _G
			xy = P.x.to_bytes(32, 'big') + P.y.to_bytes(32, 'big')
	except Exception:
		return None

	k = keccak.new(digest_bits=256)
	k.update(xy)
	addr_hex40_lower = k.hexdigest()[-40:]
	return _to_checksum_address(addr_hex40_lower)

# --- generator partii linii ---
# --- generator partii linii, zwraca (lines, bytes_read) ---
def _batched_lines(f, batch_size):
	while True:
		start = f.tell()
		chunk = list(islice(f, batch_size))
		if not chunk:
			break
		yield (chunk, f.tell() - start)

# --- praca procesu: partia -> (bytes_read, out_text) ---
def _process_batch(payload):
	lines, bytes_read = payload
	out = []
	append = out.append
	for b in lines:
		try:
			s = b.decode('ascii').strip()
		except Exception:
			continue
		# twarda walidacja: 64-znakowy hex (ETH privkey w hex)
		if len(s) != 64:
			continue
		try:
			int(s, 16)
		except ValueError:
			continue
		addr = _privhex_to_eth(s)
		if addr:
			append(f"{s} {addr}\n")
	return (bytes_read, ''.join(out))

def main():
	if not os.path.exists(INFILE):
		print(f"Brak pliku: {INFILE}", file=sys.stderr)
		sys.exit(1)

	size = os.path.getsize(INFILE)
	# tryb binarny dla dokładnego liczenia bajtów i szybkiego I/O
	with open(INFILE, 'rb', buffering=1024*1024) as fin, \
	     open(OUTFILE, 'w', buffering=1024*1024) as fout, \
	     tqdm(total=size, unit='B', unit_scale=True, miniters=1) as pbar, \
	     Pool(processes=PROCESSES, initializer=_init_worker) as pool:

		for bytes_read, result in pool.imap_unordered(
				_process_batch,
				_batched_lines(fin, BATCH_LINES),
				chunksize=1):
			pbar.update(bytes_read)
			if result:
				fout.write(result)

	# sygnał dźwiękowy na stderr (jak w oryginale)
	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
