#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 4 MB/s

import sys, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque
from tqdm import tqdm

# ---------- helpers ----------

def process_batch(lines, patt_snapshot):
	# Preliminary match; final de-duplication happens in main thread
	found = [x for x in lines if x in patt_snapshot]
	return (lines, found)

# ---------- main ----------

def main():
	if len(sys.argv) < 4:
		print(f'Usage: {sys.argv[0]} patterns_file search_in_file output_file')
		sys.exit(1)

	# Load patterns as set for O(1) lookups
	patt = set(open(sys.argv[1], 'r').read().splitlines())
	cnt = len(patt)
	print(f'Searching for {cnt} patterns...')

	infile = open(sys.argv[2], 'r')
	outfile = open(sys.argv[3], 'w')

	size = os.path.getsize(sys.argv[2])
	pbar = tqdm(total=size, unit='B', unit_scale=True)

	c = 0   # blocks processed
	r = 0   # total batches with a hit
	z = 0   # unique found
	t = 0   # position tracker

	max_workers = max(1, (os.cpu_count() or 4))
	exec = ThreadPoolExecutor(max_workers=max_workers)

	# Limit in-flight batches to avoid excessive memory use
	max_inflight = max_workers * 8
	inflight = deque()

	# Snapshot for concurrent read-only membership checks
	# Final uniqueness is resolved in the main thread against 'patt'.
	patt_snapshot = frozenset(patt)

	def submit(lines):
		return exec.submit(process_batch, lines, patt_snapshot)

	# Submit batches while reading; collect results concurrently
	while True:
		# read up to 11 lines, stop only on real EOF
		lines = []
		for _ in range(11):
			line = infile.readline()
			if not line:  # real EOF
				break
			lines.append(line.rstrip('\n'))

		if not lines:
			break

		# progress update per batch using file position
		i = infile.tell()
		q = i - t
		t = i
		if q > 0:
			pbar.update(q)
			pbar.refresh()

		# throttle in-flight tasks
		while len(inflight) >= max_inflight:
			fut = inflight.popleft()
			lines_res, found_candidates = fut.result()

			# Re-check against live 'patt' to enforce uniqueness
			found = [x for x in found_candidates if x in patt]
			if found:
				patt.difference_update(found)
				z += len(found)
				r += 1
				outfile.write('\n'.join(lines_res) + '\n')
				outfile.flush()

				# live status update
				sys.stdout.write('\0337')
				sys.stdout.write('\033[1;1H')
				sys.stdout.write('\033[2K\r')
				sys.stdout.write(f'### Found: {r} ; Unique: {z} ###\n')
				sys.stdout.write('\033[2K')
				sys.stdout.write('\0338')
				sys.stdout.flush()

				if not patt:
					print(f'Found: {r} ; Unique: {z}')
					print('\a', end='', file=sys.stderr)
					exec.shutdown(wait=False, cancel_futures=True)
					sys.exit(0)

			c += 1

		# submit next batch
		inflight.append(submit(lines))

	# Drain remaining futures
	while inflight:
		fut = inflight.popleft()
		lines_res, found_candidates = fut.result()

		# Re-check against live 'patt' to enforce uniqueness
		found = [x for x in found_candidates if x in patt]
		if found:
			patt.difference_update(found)
			z += len(found)
			r += 1
			outfile.write('\n'.join(lines_res) + '\n')
			outfile.flush()

			# live status update
			sys.stdout.write('\0337')
			sys.stdout.write('\033[1;1H')
			sys.stdout.write('\033[2K\r')
			sys.stdout.write(f'### Found: {r} ; Unique: {z} ###\n')
			sys.stdout.write('\033[2K')
			sys.stdout.write('\0338')
			sys.stdout.flush()

			if not patt:
				print(f'Found: {r} ; Unique: {z}')
				print('\a', end='', file=sys.stderr)
				exec.shutdown(wait=False, cancel_futures=True)
				sys.exit(0)

		c += 1

	print(f'Found: {r} ; Unique: {z}')
	print('\a', end='', file=sys.stderr)
	exec.shutdown(wait=True)

if __name__ == '__main__':
	main()
