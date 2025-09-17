#!/usr/bin/env python3

# pip install coincurve numba numpy

#!/usr/bin/env python3
# coding: utf-8
# Compute HASH160 = RIPEMD160(SHA256(compressed_pubkey)) for many private keys in parallel,
# using CPU (coincurve) for pubkey derivation and CUDA (numba) for SHA-256 on padded 64-byte blocks.
# Tabs for indentation as requested.

from coincurve import PrivateKey
from numba import cuda, uint8, uint32
import numpy as np
import hashlib
import math
import sys
from concurrent.futures import ThreadPoolExecutor

# --- SHA256 constants ---
K = np.array([
	0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
	0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
	0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
	0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
	0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
	0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
	0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
	0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
], dtype=np.uint32)

# Copy constants to device global memory
d_K = cuda.to_device(K)

@cuda.jit(device=True, inline=True)
def rotr(x, n):
	return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF

@cuda.jit
def sha256_kernel(blocks, out_digests, Kdev):
	# blocks: (N, 64) uint8
	# out_digests: (N, 32) uint8
	i = cuda.grid(1)
	n = blocks.shape[0]
	if i >= n:
		return

	# Load the single 64-byte block for this thread
	# Prepare W[0..63]
	W = cuda.local.array(64, uint32)
	for t in range(16):
		j = t * 4
		W[t] = (uint32(blocks[i, j]) << 24) | (uint32(blocks[i, j+1]) << 16) | (uint32(blocks[i, j+2]) << 8) | (uint32(blocks[i, j+3]))

	for t in range(16, 64):
		s0 = (rotr(W[t-15], 7) ^ rotr(W[t-15], 18) ^ (W[t-15] >> 3)) & 0xFFFFFFFF
		s1 = (rotr(W[t-2], 17) ^ rotr(W[t-2], 19) ^ (W[t-2] >> 10)) & 0xFFFFFFFF
		W[t] = (W[t-16] + s0 + W[t-7] + s1) & 0xFFFFFFFF

	# initial hash values (first 32 bits of the fractional parts of the square roots of the first 8 primes)
	a = uint32(0x6a09e667)
	b = uint32(0xbb67ae85)
	c = uint32(0x3c6ef372)
	d = uint32(0xa54ff53a)
	e = uint32(0x510e527f)
	f = uint32(0x9b05688c)
	g = uint32(0x1f83d9ab)
	h = uint32(0x5be0cd19)

	for t in range(64):
		S1 = (rotr(e,6) ^ rotr(e,11) ^ rotr(e,25)) & 0xFFFFFFFF
		ch = (e & f) ^ ((~e) & g)
		temp1 = (h + S1 + ch + Kdev[t] + W[t]) & 0xFFFFFFFF
		S0 = (rotr(a,2) ^ rotr(a,13) ^ rotr(a,22)) & 0xFFFFFFFF
		maj = (a & b) ^ (a & c) ^ (b & c)
		temp2 = (S0 + maj) & 0xFFFFFFFF

		h = g
		g = f
		f = e
		e = (d + temp1) & 0xFFFFFFFF
		d = c
		c = b
		b = a
		a = (temp1 + temp2) & 0xFFFFFFFF

	# Add this chunk's hash to result so far
	h0 = uint32(0x6a09e667) + a
	h1 = uint32(0xbb67ae85) + b
	h2 = uint32(0x3c6ef372) + c
	h3 = uint32(0xa54ff53a) + d
	h4 = uint32(0x510e527f) + e
	h5 = uint32(0x9b05688c) + f
	h6 = uint32(0x1f83d9ab) + g
	h7 = uint32(0x5be0cd19) + h

	# store digest big-endian
	out_idx = i * 32
	# write into out_digests[i, 0..31]
	# h0..h7 as 4 bytes each
	tmp = [h0, h1, h2, h3, h4, h5, h6, h7]
	for k in range(8):
		val = tmp[k]
		j = k*4
		out_digests[i, j]   = uint8((val >> 24) & 0xFF)
		out_digests[i, j+1] = uint8((val >> 16) & 0xFF)
		out_digests[i, j+2] = uint8((val >> 8) & 0xFF)
		out_digests[i, j+3] = uint8(val & 0xFF)


def privhex_to_compressed_pubkey(privhex):
	# returns bytes of compressed pubkey (33 bytes)
	priv = bytes.fromhex(privhex)
	pk = PrivateKey(priv)
	return pk.public_key.format(compressed=True)


def make_padded_block_for_sha256(msg_bytes):
	# msg_bytes: bytes, length <= 55 for single-block (we assume compressed pubkey 33 bytes)
	ml = len(msg_bytes)
	if ml > 55:
		raise ValueError("message too long for single-block padding used here")
	# start with msg
	block = bytearray(64)
	block[0:ml] = msg_bytes
	# append 0x80
	block[ml] = 0x80
	# last 8 bytes: 64-bit big-endian message length in bits
	bit_len = ml * 8
	block[56:64] = bit_len.to_bytes(8, 'big')
	return bytes(block)


def batch_hash160(privhex_list, threads=8, batch_size_gpu=1<<16):
	# privhex_list: iterable of hex strings
	# Step 1: compute compressed pubkeys in parallel on CPU
	privhex_list = list(privhex_list)
	n = len(privhex_list)

	with ThreadPoolExecutor(max_workers=threads) as ex:
		pubkeys = list(ex.map(privhex_to_compressed_pubkey, privhex_list))

	# Step 2: create padded 64-byte blocks for each pubkey
	blocks = np.empty((n, 64), dtype=np.uint8)
	for i, pk in enumerate(pubkeys):
		blocks[i] = np.frombuffer(make_padded_block_for_sha256(pk), dtype=np.uint8)

	# Step 3: process in GPU-friendly chunks
	results_hash160 = [None] * n
	idx = 0
	while idx < n:
		chunk = blocks[idx: idx + batch_size_gpu]
		m = chunk.shape[0]
		# device arrays
		dev_blocks = cuda.to_device(chunk)
		dev_out = cuda.device_array((m, 32), dtype=np.uint8)
		# launch kernel
		threads_per_block = 256
		blocks_per_grid = (m + threads_per_block - 1) // threads_per_block
		sha256_kernel[blocks_per_grid, threads_per_block](dev_blocks, dev_out, d_K)
		# copy back
		out_sha = dev_out.copy_to_host()  # shape (m,32)
		# compute RIPEMD160 on host from sha digests
		for j in range(m):
			sha_digest = bytes(out_sha[j].tolist())
			rip = hashlib.new('ripemd160', sha_digest).digest()
			results_hash160[idx + j] = rip.hex()
		idx += m

	return results_hash160


if __name__ == '__main__':
	# small example
	example_privs = [
		'1' * 64,  # NOT a real private key necessarily; replace with your list
		'2' * 64,
		'3' * 64,
	]
	# validate hex lengths
	example_privs = [p.zfill(64) for p in example_privs]

	out = batch_hash160(example_privs, threads=8, batch_size_gpu=1024)
	for p, h in zip(example_privs, out):
		print(p, '->', h)
