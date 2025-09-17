#!/usr/bin/env python3
# example_usage.py
from ripemd160_cuda import ripemd160_cuda, benchmark_cuda
import binascii

# Example usage
if __name__ == "__main__":
	# Single input test
	test_inputs = ["hello world", "bitcoin", "test input"]
	hashes = ripemd160_cuda(test_inputs)
	
	print("RIPEMD-160 Hashes:")
	for input_str, hash_bytes in zip(test_inputs, hashes):
		print(f"{input_str}: {binascii.hexlify(hash_bytes).decode()}")
	
	# Benchmark
	print("\n" + "="*50)
	benchmark_inputs = [f"benchmark_{i}" for i in range(1000000)]
	benchmark_cuda(benchmark_inputs)
