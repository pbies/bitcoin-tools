#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cuda_sha256_demo.py
Educational GPU implementation of SHA-256 (single-block messages only) using Numba CUDA.
This is a pedagogical example showing how to:
 - implement SHA-256 core operations as device functions,
 - run a CUDA kernel that computes SHA-256 for many independent small messages in parallel,
 - transfer data to/from the GPU and verify results against Python's hashlib.

SAFETY & LIMITS
- THIS IS FOR EDUCATIONAL / BENIGN PURPOSES ONLY.
- The kernel supports only single-block messages (<= 55 bytes). It will refuse longer messages.
- This is NOT an optimized production-grade SHA-256; it's written for clarity, correctness, and teaching.
- Do NOT use this to brute-force keys, crack passwords, or otherwise perform malicious activity.
- Requirements: Python, Numba, NumPy, a CUDA-capable NVIDIA GPU + drivers.

Usage
-----
1) pip install numba numpy
2) Run: python3 cuda_sha256_demo.py
It will compute SHA-256 over a batch of random records and compare results with hashlib for correctness.
"""

from __future__ import annotations
import sys, time, math
import numpy as np
from numba import cuda, uint32, uint8, int32, types

# --------------- Configuration -----------------
N_RECORDS = 1 << 18    # ~262k records by default (reduce if GPU memory limited)
RECORD_LEN = 32        # bytes per record (must be <= 55 for single-block padding)
TPB = 128              # threads per block
OUT_FILE = 'cuda_sha256_hashes.npy'
# ------------------------------------------------

if RECORD_LEN > 55:
	raise SystemExit("RECORD_LEN must be <= 55 for this single-block demo. Reduce RECORD_LEN and retry.")

# SHA-256 constants (first 32 bits of the fractional parts of the cube roots of the first 64 primes)
_K = np.array([
	0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
	0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
	0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
	0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
	0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
	0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
	0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
	0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2,
], dtype=np.uint32)

# Copy constants to device global constant memory
_K_device = cuda.to_device(_K)

@cuda.jit(device=True, inline=True)
def rotr(x, n):
	# rotate right for uint32
	return ((x >> n) | (x << (32 - n))) & uint32(0xFFFFFFFF)

@cuda.jit(device=True, inline=True)
def ch(x, y, z):
	return (x & y) ^ (~x & z)

@cuda.jit(device=True, inline=True)
def maj(x, y, z):
	return (x & y) ^ (x & z) ^ (y & z)

@cuda.jit(device=True, inline=True)
def big_sigma0(x):
	return rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22)

@cuda.jit(device=True, inline=True)
def big_sigma1(x):
	return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25)

@cuda.jit(device=True, inline=True)
def small_sigma0(x):
	return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3)

@cuda.jit(device=True, inline=True)
def small_sigma1(x):
	return rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10)

@cuda.jit
def kernel_sha256_single_block(inp, inp_len, out_hash):
	"""
	Compute SHA-256 for each record in inp (single 512-bit block per message).
	inp: uint8 array shape (N_RECORDS, RECORD_LEN)
	inp_len: int32 array shape (N_RECORDS,) indicating length of each record
	out_hash: uint32 array shape (N_RECORDS, 8) - 8 uint32 words of the digest
	"""
	i = cuda.grid(1)
	if i >= inp.shape[0]:
		return

	msg_len = inp_len[i]
	if msg_len > 55:
		# we don't handle multi-block messages in this demo
		for j in range(8):
			out_hash[i, j] = uint32(0xFFFFFFFF)
		return

	# Prepare the 512-bit block (64 bytes)
	block = cuda.local.array(64, uint8)
	# zero-fill
	for j in range(64):
		block[j] = uint8(0)

	# copy message bytes
	for j in range(msg_len):
		block[j] = inp[i, j]

	# append 0x80
	block[msg_len] = uint8(0x80)

	# append message length in bits as 64-bit big-endian at block[56..63]
	bit_len = uint32(msg_len * 8)  # safe for msg_len <= 2^32-1 for this demo
	# store as 64-bit big-endian (high 32 bits zero)
	block[56] = uint8(0)
	block[57] = uint8(0)
	block[58] = uint8(0)
	block[59] = uint8(0)
	block[60] = uint8((bit_len >> 24) & 0xFF)
	block[61] = uint8((bit_len >> 16) & 0xFF)
	block[62] = uint8((bit_len >> 8) & 0xFF)
	block[63] = uint8(bit_len & 0xFF)

	# prepare message schedule w[0..63] (uint32 words)
	w = cuda.local.array(64, uint32)
	# fill w[0..15] from block (big-endian)
	for t in range(16):
		idx = t * 4
		w[t] = (uint32(block[idx]) << 24) | (uint32(block[idx+1]) << 16) | (uint32(block[idx+2]) << 8) | uint32(block[idx+3])

	# extend w[16..63]
	for t in range(16, 64):
		s0 = small_sigma0(w[t-15])
		s1 = small_sigma1(w[t-2])
		w[t] = (w[t-16] + s0 + w[t-7] + s1) & uint32(0xFFFFFFFF)

	# initial hash values (first 32 bits of fractional parts of the square roots of the first 8 primes)
	a = uint32(0x6a09e667)
	b = uint32(0xbb67ae85)
	c = uint32(0x3c6ef372)
	d = uint32(0xa54ff53a)
	e = uint32(0x510e527f)
	f = uint32(0x9b05688c)
	g = uint32(0x1f83d9ab)
	h = uint32(0x5be0cd19)

	# compression function main loop
	for t in range(64):
		t1 = (h + big_sigma1(e) + ch(e, f, g) + _K_device[t] + w[t]) & uint32(0xFFFFFFFF)
		t2 = (big_sigma0(a) + maj(a, b, c)) & uint32(0xFFFFFFFF)
		h = g
		g = f
		f = e
		e = (d + t1) & uint32(0xFFFFFFFF)
		d = c
		c = b
		b = a
		a = (t1 + t2) & uint32(0xFFFFFFFF)

	# compute final hash value (add to initial hashes)
	out_hash[i, 0] = (uint32(0x6a09e667) + a) & uint32(0xFFFFFFFF)
	out_hash[i, 1] = (uint32(0xbb67ae85) + b) & uint32(0xFFFFFFFF)
	out_hash[i, 2] = (uint32(0x3c6ef372) + c) & uint32(0xFFFFFFFF)
	out_hash[i, 3] = (uint32(0xa54ff53a) + d) & uint32(0xFFFFFFFF)
	out_hash[i, 4] = (uint32(0x510e527f) + e) & uint32(0xFFFFFFFF)
	out_hash[i, 5] = (uint32(0x9b05688c) + f) & uint32(0xFFFFFFFF)
	out_hash[i, 6] = (uint32(0x1f83d9ab) + g) & uint32(0xFFFFFFFF)
	out_hash[i, 7] = (uint32(0x5be0cd19) + h) & uint32(0xFFFFFFFF)


def make_input(n_records, rec_len):
	# deterministic pseudo-random data for reproducibility
	rng = np.random.RandomState(12345)
	arr = rng.randint(0, 256, size=(n_records, rec_len), dtype=np.uint8)
	lengths = np.full((n_records,), rec_len, dtype=np.int32)
	return arr, lengths

def sha256_host_batch(inp, inp_len):
	# compute SHA-256 on host using hashlib for verification
	import hashlib
	out = np.zeros((inp.shape[0], 8), dtype=np.uint32)
	for i in range(inp.shape[0]):
		msg = bytes(inp[i, :inp_len[i]].tolist())
		d = hashlib.sha256(msg).digest()
		# digest is big-endian 32 bytes -> convert to 8 uint32 words big-endian
		for j in range(8):
			out[i, j] = int.from_bytes(d[j*4:(j+1)*4], 'big', signed=False)
	return out

def main():
	print("CUDA SHA-256 demo (single-block messages only)")
	try:
		from numba import cuda as _cuda
		if not _cuda.is_available():
			print("CUDA not available. Ensure drivers and a CUDA-capable GPU are present.")
			return 2
	except Exception as e:
		print("Numba CUDA import error:", e)
		return 2

	n = N_RECORDS
	rec_len = RECORD_LEN
	print(f'Preparing {n:,} records, each {rec_len} bytes')
	inp, inp_len = make_input(n, rec_len)

	# allocate device memory
	inp_dev = cuda.to_device(inp)
	inp_len_dev = cuda.to_device(inp_len)
	out_dev = cuda.device_array((n, 8), dtype=np.uint32)

	blocks = (n + TPB - 1) // TPB
	print(f'Launching kernel with blocks={blocks}, threads_per_block={TPB}')
	start = time.time()
	kernel_sha256_single_block[blocks, TPB](inp_dev, inp_len_dev, out_dev)
	cuda.synchronize()
	elapsed = time.time() - start
	print(f'Kernel finished in {elapsed:.3f}s')

	out = out_dev.copy_to_host()
	# optionally save raw uint32 words
	np.save(OUT_FILE, out)
	print(f'Results saved to {OUT_FILE} (shape={out.shape})')

	# verify first 100 items against hashlib
	print('Verifying first 100 outputs against hashlib...')
	host_ref = sha256_host_batch(inp[:100], inp_len[:100])
	mismatch = 0
	for i in range(100):
		if not np.array_equal(out[i], host_ref[i]):
			mismatch += 1
			print(f'! mismatch at index {i}')
	if mismatch == 0:
		print('All first 100 hashes match hashlib.sha256() — good.')
	else:
		print(f'Found {mismatch} mismatches in first 100 (unexpected).')

	# print sample digest hex for first 5 records
	print('Sample digest hex (first 5):')
	for i in range(5):
		hwords = out[i]
		# convert big-endian uint32 words to bytes and hex
		b = bytearray()
		for w in hwords:
			b.extend(int(w).to_bytes(4, 'big'))
		print(f'{i:3d}: {bytes(b).hex()}')

	return 0

if __name__ == '__main__':
	sys.exit(main() or 0)
