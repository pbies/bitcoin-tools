#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import sys

MAX_B = 1_000_000_000
CHUNK_SIZE = 1_000_000

def worker(args):
	start_x, end_x = args
	out = []

	for x in range(start_x, end_x):
		a = (x * 6) - 1
		b = (x * 6) + 1

		if a % 5 != 0:
			out.append(f"{a}\n")

		if b % 5 != 0:
			out.append(f"{b}\n")

		if b > MAX_B:
			break

	return "".join(out)

def generate_ranges():
	max_x = (MAX_B // 6) + 2
	for start in range(2, max_x, CHUNK_SIZE):
		end = min(start + CHUNK_SIZE, max_x)
		yield (start, end)

def main():
	with Pool(cpu_count()) as pool, open("primes02.txt", "w") as o:
		total_chunks = ((MAX_B // 6) + 2 + CHUNK_SIZE - 1) // CHUNK_SIZE

		for result in tqdm(
			pool.imap_unordered(worker, generate_ranges(), chunksize=1),
			total=total_chunks
		):
			o.write(result)

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
