#!/usr/bin/env python3

import sys

B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def b58dec(s):
	n = 0
	for c in s:
		n = n * 58 + B58.index(c)
	return n.to_bytes(25, 'big')

def main():
	input_file = 'addrs.txt'
	output_file = 'hashes.txt'

	with open(input_file, 'r') as f:
		lines = [l.strip() for l in f if l.strip()]

	total = len(lines)
	errors = 0

	with open(output_file, 'w') as out:
		for i, addr in enumerate(lines, 1):
			try:
				raw = b58dec(addr)
				out.write(raw[1:21].hex() + '\n')
			except Exception:
				errors += 1
				sys.stderr.write(f'skip: {addr}\n')

			if i % 50000 == 0 or i == total:
				pct = i * 100 // total
				bar = '#' * (pct // 2) + '-' * (50 - pct // 2)
				sys.stderr.write(f'\r[{bar}] {pct:3d}% {i}/{total}')
				sys.stderr.flush()

	sys.stderr.write(f'\ndone. errors: {errors}\n')

main()
