#!/usr/bin/env python3
"""
RIPEMD-160 CUDA Implementation
GPU-accelerated RIPEMD-160 hashing for large-scale operations
"""

import numpy as np
import numba.cuda as cuda
from numba import uint32, uint8, int32
import time
import binascii
import argparse

# CUDA configuration
THREADS_PER_BLOCK = 256
BLOCKS = 1024

# RIPEMD-160 constants
RIPEMD160_BLOCK_SIZE = 64
RIPEMD160_DIGEST_SIZE = 20

# RIPEMD-160 rotation constants
def ROL(x, n):
	return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

@cuda.jit(device=True)
def device_ROL(x, n):
	return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

@cuda.jit
def ripemd160_kernel(input_data, input_lengths, output_hashes):
	"""
	CUDA kernel for RIPEMD-160 hashing
	input_data: flat array of all input bytes
	input_lengths: array of lengths for each input
	output_hashes: output array for 20-byte hashes
	"""
	idx = cuda.grid(1)
	total_inputs = input_lengths.size
	
	if idx < total_inputs:
		# Calculate start position in input_data
		start_idx = 0
		for i in range(idx):
			start_idx += input_lengths[i]
		
		current_length = input_lengths[idx]
		
		# Initialize RIPEMD-160 state
		h0 = 0x67452301
		h1 = 0xEFCDAB89
		h2 = 0x98BADCFE
		h3 = 0x10325476
		h4 = 0xC3D2E1F0
		
		# Pre-processing: padding
		original_bit_length = current_length * 8
		padding_length = (56 - (current_length + 1) % 64) % 64
		
		total_length = current_length + padding_length + 9
		padded_data = cuda.local.array(128, uint8)  # Enough for padded message
		
		# Copy original data
		for i in range(current_length):
			padded_data[i] = input_data[start_idx + i]
		
		# Add padding
		padded_data[current_length] = 0x80
		for i in range(current_length + 1, current_length + padding_length + 1):
			padded_data[i] = 0
		
		# Add length in bits (little-endian)
		for i in range(8):
			padded_data[current_length + padding_length + 1 + i] = (original_bit_length >> (i * 8)) & 0xFF
		
		# Process message in 64-byte chunks
		num_chunks = total_length // 64
		
		for chunk in range(num_chunks):
			chunk_start = chunk * 64
			
			# Prepare message schedule
			w = cuda.local.array(16, uint32)
			for i in range(16):
				w[i] = (padded_data[chunk_start + i*4 + 3] << 24) | \
					   (padded_data[chunk_start + i*4 + 2] << 16) | \
					   (padded_data[chunk_start + i*4 + 1] << 8) | \
					   padded_data[chunk_start + i*4]
			
			# Initialize working variables
			a, b, c, d, e = h0, h1, h2, h3, h4
			a2, b2, c2, d2, e2 = h0, h1, h2, h3, h4
			
			# Main RIPEMD-160 compression function
			# Left round functions
			for i in range(16):
				if i < 4:
					f = (b ^ c ^ d)
					k = 0x00000000
				elif i < 8:
					f = (b & c) | ((~b) & d)
					k = 0x5A827999
				elif i < 12:
					f = (b | (~c)) ^ d
					k = 0x6ED9EBA1
				else:
					f = (b & d) | (c & (~d))
					k = 0x8F1BBCDC
				
				t = (device_ROL(a + f + e + k + w[i], [5, 7, 4, 6][i % 4])) + b
				a, b, c, d, e = e, t, a, device_ROL(b, 10), c
			
			# Right round functions
			for i in range(16):
				if i < 4:
					f = (b2 ^ c2 ^ d2)
					k = 0x50A28BE6
				elif i < 8:
					f = (b2 & d2) | (c2 & (~d2))
					k = 0x5C4DD124
				elif i < 12:
					f = (b2 | (~c2)) ^ d2
					k = 0x6D703EF3
				else:
					f = (b2 & c2) | ((~b2) & d2)
					k = 0x00000000
				
				t = (device_ROL(a2 + f + e2 + k + w[[5, 14, 7, 0, 9, 2, 11, 4, 13, 6, 15, 8, 1, 10, 3, 12][i]], 
							   [8, 9, 9, 11, 13, 15, 15, 5, 7, 7, 8, 11, 14, 14, 12, 6][i])) + b2
				a2, b2, c2, d2, e2 = e2, t, a2, device_ROL(b2, 10), c2
			
			# Combine results
			t = h1 + c + d2
			h1 = h2 + d + e2
			h2 = h3 + e + a2
			h3 = h4 + a + b2
			h4 = h0 + b + c2
			h0 = t
		
		# Store final hash
		output_start = idx * 20
		final_hash = [h0, h1, h2, h3, h4]
		
		for i in range(5):
			output_hashes[output_start + i*4] = final_hash[i] & 0xFF
			output_hashes[output_start + i*4 + 1] = (final_hash[i] >> 8) & 0xFF
			output_hashes[output_start + i*4 + 2] = (final_hash[i] >> 16) & 0xFF
			output_hashes[output_start + i*4 + 3] = (final_hash[i] >> 24) & 0xFF

def prepare_inputs(input_strings):
	"""Prepare input data for CUDA processing"""
	all_data = []
	lengths = []
	
	for s in input_strings:
		if isinstance(s, str):
			data = s.encode('utf-8')
		else:
			data = s
		
		all_data.extend(data)
		lengths.append(len(data))
	
	return np.array(all_data, dtype=np.uint8), np.array(lengths, dtype=np.int32)

def ripemd160_cuda(input_strings):
	"""Main function to compute RIPEMD-160 hashes using CUDA"""
	if not input_strings:
		return []
	
	# Prepare input data
	input_data, input_lengths = prepare_inputs(input_strings)
	num_inputs = len(input_strings)
	
	# Allocate device memory
	d_input_data = cuda.to_device(input_data)
	d_input_lengths = cuda.to_device(input_lengths)
	d_output = cuda.device_array(num_inputs * 20, dtype=np.uint8)
	
	# Calculate grid size
	grid_size = (num_inputs + THREADS_PER_BLOCK - 1) // THREADS_PER_BLOCK
	
	# Launch kernel
	ripemd160_kernel[grid_size, THREADS_PER_BLOCK](d_input_data, d_input_lengths, d_output)
	
	# Copy results back
	results = d_output.copy_to_host()
	
	# Format results
	hashes = []
	for i in range(num_inputs):
		hash_start = i * 20
		hash_bytes = bytes(results[hash_start:hash_start + 20])
		hashes.append(hash_bytes)
	
	return hashes

def benchmark_cuda(input_strings, iterations=10):
	"""Benchmark CUDA performance"""
	print(f"Benchmarking with {len(input_strings):,} inputs...")
	
	warmup = ripemd160_cuda(input_strings[:1000])  # Warmup
	
	times = []
	for i in range(iterations):
		start_time = time.time()
		hashes = ripemd160_cuda(input_strings)
		end_time = time.time()
		times.append(end_time - start_time)
		
		if i == 0:
			print(f"First hash: {binascii.hexlify(hashes[0]).decode()}")
	
	avg_time = np.mean(times[1:])  # Skip first run
	hashes_per_second = len(input_strings) / avg_time
	
	print(f"Average time: {avg_time:.4f} seconds")
	print(f"Hashes per second: {hashes_per_second:,.0f}")
	print(f"Throughput: {hashes_per_second / 1e6:.2f} MHash/s")
	
	return hashes_per_second

def main():
	parser = argparse.ArgumentParser(description='RIPEMD-160 CUDA Implementation')
	parser.add_argument('--benchmark', type=int, default=1000000,
					   help='Number of inputs for benchmarking')
	parser.add_argument('--input', type=str, nargs='+',
					   help='Input strings to hash')
	parser.add_argument('--file', type=str,
					   help='File containing inputs (one per line)')
	
	args = parser.parse_args()
	
	if args.input:
		# Process provided inputs
		inputs = args.input
		print(f"Processing {len(inputs)} inputs...")
		
		start_time = time.time()
		hashes = ripemd160_cuda(inputs)
		end_time = time.time()
		
		for i, (input_str, hash_bytes) in enumerate(zip(inputs, hashes)):
			print(f"{input_str} -> {binascii.hexlify(hash_bytes).decode()}")
		
		print(f"\nTime: {end_time - start_time:.4f} seconds")
		print(f"Speed: {len(inputs) / (end_time - start_time):.0f} hashes/sec")
	
	elif args.file:
		# Process file inputs
		try:
			with open(args.file, 'r') as f:
				inputs = [line.strip() for line in f.readlines() if line.strip()]
			
			print(f"Processing {len(inputs):,} inputs from file...")
			
			start_time = time.time()
			hashes = ripemd160_cuda(inputs)
			end_time = time.time()
			
			# Save results
			output_file = args.file + '.hashes'
			with open(output_file, 'w') as f:
				for input_str, hash_bytes in zip(inputs, hashes):
					f.write(f"{input_str},{binascii.hexlify(hash_bytes).decode()}\n")
			
			print(f"Results saved to {output_file}")
			print(f"Time: {end_time - start_time:.4f} seconds")
			print(f"Speed: {len(inputs) / (end_time - start_time):.0f} hashes/sec")
			
		except Exception as e:
			print(f"Error processing file: {e}")
	
	else:
		# Run benchmark
		print("No inputs provided, running benchmark...")
		benchmark_size = args.benchmark
		
		# Generate test data
		test_inputs = [f"test_input_{i}" for i in range(benchmark_size)]
		
		benchmark_cuda(test_inputs)

if __name__ == "__main__":
	# Check if CUDA is available
	if not cuda.is_available():
		print("CUDA is not available. Please check your CUDA installation.")
		exit(1)
	
	print(f"CUDA devices available: {cuda.gpus.len()}")
	for i in range(len(cuda.gpus)):
		with cuda.gpus[i]:
			print(f"Device {i}: {cuda.get_current_device().name}")
	
	main()
