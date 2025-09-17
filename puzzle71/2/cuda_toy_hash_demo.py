#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cuda_toy_hash_demo.py
Edukacyjny przykład: jak uruchomić kernel CUDA (Numba) z Pythona.
Robi prostą, niekryptograficzną funkcję FNV-1a (64-bit) nad wejściową tablicą
bajtów i zapisuje wynik do tablicy wyników.

NIE STOSUJ TEGO DO PRZESZUKIWANIA PRZESTRZENI KLUCZY — to demonstracja techniczna.
"""

from __future__ import annotations
import sys, os, time, math, random
import numpy as np
from numba import cuda, uint64, uint8, int32

# -------------------- Konfiguracja --------------------
# Liczba "rekordów" (wejściowych ciągów bajtów) do obliczenia na GPU
N_RECORDS = 1 << 20  # 1M (zmniejsz jeśli pamięć GPU nie wystarcza)
RECORD_LEN = 32      # długość każdego rekordu w bajtach (np. 32)
TPB = 256            # threads per block
OUT_FILE = 'toy_gpu_hashes.npy'
# -----------------------------------------------------

@cuda.jit(device=True, inline=True)
def fnv1a64(data, length):
	"""
	Simple FNV-1a 64-bit (non-cryptographic). Returns uint64.
	Used only as a demo of per-thread work on GPU.
	"""
	# constants
	hash_ = uint64(0xcbf29ce484222325)
	fnv_prime = uint64(0x100000001b3)
	for i in range(length):
		hash_ = hash_ ^ uint64(data[i])
		hash_ = uint64((hash_ * fnv_prime) & 0xFFFFFFFFFFFFFFFF)
	return hash_

@cuda.jit
def kernel_compute_hashes(inp, out, rec_len):
	"""
	inp: uint8 array of shape (N_RECORDS, RECORD_LEN)
	out: uint64 array shape (N_RECORDS,)
	"""
	i = cuda.grid(1)
	if i >= out.shape[0]:
		return

	# local buffer: read RECORD_LEN bytes
	# Numba does not allow variable-length local arrays; read directly
	# into a small Python-level loop accessing inp.
	# For performance-critical code, consider coalesced access patterns.
	tmp = cuda.local.array(64, uint8)  # max RECORD_LEN supported = 64 here
	for j in range(rec_len):
		tmp[j] = inp[i, j]

	h = fnv1a64(tmp, rec_len)
	out[i] = h

def make_input(n_records, rec_len):
	# For demo: create deterministic pseudorandom inputs (so runs are reproducible)
	rng = np.random.RandomState(42)
	arr = rng.randint(0, 256, size=(n_records, rec_len), dtype=np.uint8)
	return arr

def main():
	print('Edukacyjny CUDA demo (Numba) — FNV-1a 64-bit on toy dataset')
	try:
		from numba import cuda as _cuda
		if not _cuda.is_available():
			print('CUDA nie jest dostępne. Upewnij się że masz sterowniki i kartę NVIDIA.')
			return 2
	except Exception as e:
		print('Numba CUDA import error:', e)
		return 2

	# small safety checks
	n = N_RECORDS
	if n > 4_000_000:
		print('N_RECORDS jest duże — zmniejszamy do 4M dla bezpieczeństwa.')
		n = 4_000_000

	rec_len = RECORD_LEN
	if rec_len > 64:
		print('RECORD_LEN za duży dla tego demo (max 64). Ustaw na <= 64.')
		return 2

	print(f'Preparing input: records={n:,}, record_len={rec_len}')
	inp = make_input(n, rec_len)

	# allocate device arrays
	inp_device = cuda.to_device(inp)
	out_device = cuda.device_array(shape=(n,), dtype=np.uint64)

	# launch kernel
	blocks = (n + TPB - 1) // TPB
	print(f'Launching kernel: blocks={blocks}, tpb={TPB}')
	start = time.time()
	kernel_compute_hashes[blocks, TPB](inp_device, out_device, rec_len)
	cuda.synchronize()
	elapsed = time.time() - start
	print(f'Kernel finished in {elapsed:.3f}s')

	# copy results back and save
	out = out_device.copy_to_host()
	np.save(OUT_FILE, out)
	print(f'Results saved to {OUT_FILE} (shape={out.shape})')

	# sample output
	print('Sample hashes (first 10):')
	for i in range(min(10, out.shape[0])):
		print(f'{i:3d}: {out[i]:016x}')

	return 0

if __name__ == '__main__':
	sys.exit(main() or 0)
