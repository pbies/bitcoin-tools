#!/usr/bin/env python3

import sys

def reverse_file_bytes(input_path, output_path):
	with open(input_path, 'rb') as f:
		data = f.read()
	
	reversed_data = data[::-1]
	
	with open(output_path, 'wb') as f:
		f.write(reversed_data)
	
	print(f"Reversed {len(data)} bytes -> {output_path}")

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Usage: python reverse_bytes.py <input_file> <output_file>")
		sys.exit(1)
	
	reverse_file_bytes(sys.argv[1], sys.argv[2])
