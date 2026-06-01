#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sort_hashes.py - High-performance MD5 hash sorting and deduplication.
Uses multiprocessing (bypasses GIL) + mmap + LZ4 compressed temp files.
"""

import os
import sys
import lz4.frame
import heapq
import tempfile
import argparse
import time
import mmap
from multiprocessing import Pool, cpu_count, Queue

# -----------------------------------------------
# Default settings
# -----------------------------------------------
CHUNK_SIZE   = 3000000
NUM_WORKERS  = cpu_count()
TEMP_DIR	 = "."
LZ4_LEVEL	= 1
MERGE_BATCH  = 64

_t0 = time.time()

def log(msg):
	elapsed = time.time() - _t0
	print("[%6.1fs] %s" % (elapsed, msg))
	sys.stdout.flush()

# -----------------------------------------------
# Worker: runs in a separate process (no GIL!)
# -----------------------------------------------
def process_chunk(args):
	chunk_id, lines, tmp_dir = args

	t = time.time()
	s = set()
	for line in lines:
		if line:
			s.add(line)

	unique = sorted(s)  # bytes comparison = LC_ALL=C byte order

	tmp_path = os.path.join(tmp_dir, "chunk_%06d.lz4" % chunk_id)
	data = b"\n".join(unique) + b"\n" if unique else b""

	with lz4.frame.open(tmp_path, mode="wb",
						compression_level=LZ4_LEVEL,
						block_size=lz4.frame.BLOCKSIZE_MAX4MB) as f:
		f.write(data)

	elapsed = time.time() - t
	return (chunk_id, len(lines), len(unique), elapsed, tmp_path)

# -----------------------------------------------
# Read file into chunks via mmap
# -----------------------------------------------
def iter_chunks(input_file, chunk_size):
	chunk = []
	chunk_id = 0
	with open(input_file, "rb") as fh:
		mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
		for raw_line in iter(mm.readline, b""):
			chunk.append(raw_line.rstrip(b'\r\n'))
			if len(chunk) >= chunk_size:
				yield chunk_id, chunk
				chunk_id += 1
				chunk = []
		mm.close()
	if chunk:
		yield chunk_id, chunk

# -----------------------------------------------
# Step 1: parallel sort with multiprocessing
# -----------------------------------------------
def split_and_sort(input_file, tmp_dir, chunk_size, num_workers):
	log("[1/2] Sorting '%s' (chunk=%d lines, workers=%d)..." % (input_file, chunk_size, num_workers))

	def task_gen():
		for chunk_id, chunk in iter_chunks(input_file, chunk_size):
			yield (chunk_id, chunk, tmp_dir)

	tmp_files = []
	with Pool(processes=num_workers) as pool:
		for chunk_id, total, unique, elapsed, tmp_path in pool.imap_unordered(process_chunk, task_gen(), chunksize=1):
			log("  [chunk %4d] %8d lines -> %7d unique  [%.1fs]"
				% (chunk_id, total, unique, elapsed))
			tmp_files.append(tmp_path)

	tmp_files.sort()
	log("  Temp files created: %d" % len(tmp_files))
	return tmp_files

# -----------------------------------------------
# Read lines from LZ4 tmp file
# -----------------------------------------------
def lz4_line_iter(path):
	with lz4.frame.open(path, mode="rb") as f:
		buf = b""
		while True:
			block = f.read(1 << 20)
			if not block:
				break
			buf += block
			lines = buf.split(b"\n")
			buf = lines[-1]
			for line in lines[:-1]:
				if line:
					yield line
		if buf:
			yield buf

# -----------------------------------------------
# Merge a batch of sorted LZ4 files
# -----------------------------------------------
def merge_batch(tmp_files, out_path, compressed=True):
	iters = [lz4_line_iter(p) for p in tmp_files]
	prev = None
	total = 0

	if compressed:
		out_cm = lz4.frame.open(out_path, mode="wb",
								compression_level=LZ4_LEVEL,
								block_size=lz4.frame.BLOCKSIZE_MAX4MB)
	else:
		out_cm = open(out_path, "wb", buffering=1 << 23)

	with out_cm as out:
		buf = []
		for line in heapq.merge(*iters):
			if line != prev:
				buf.append(line)
				prev = line
				total += 1
				if len(buf) >= 50000:
					out.write(b"\n".join(buf) + b"\n")
					buf = []
		if buf:
			out.write(b"\n".join(buf) + b"\n")

	return total, out_path

# -----------------------------------------------
# Step 2: two-level merge
# -----------------------------------------------
def merge_sorted_files(tmp_files, output_file, tmp_dir):
	log("[2/2] Merging %d files -> '%s'..." % (len(tmp_files), output_file))

	if len(tmp_files) > MERGE_BATCH:
		log("  Two-level merge: batches of %d" % MERGE_BATCH)
		batches = [tmp_files[i:i+MERGE_BATCH]
				   for i in range(0, len(tmp_files), MERGE_BATCH)]
		pass1_files = []
		for i, batch in enumerate(batches):
			p = os.path.join(tmp_dir, "merged_%04d.lz4" % i)
			count, path = merge_batch(batch, p, compressed=True)
			pass1_files.append(path)
			log("  Batch %d: %d unique" % (i, count))

		log("  Final merge of %d files..." % len(pass1_files))
		total, _ = merge_batch(pass1_files, output_file, compressed=False)
	else:
		total, _ = merge_batch(tmp_files, output_file, compressed=False)

	return total

# -----------------------------------------------
# Main
# -----------------------------------------------
def main():
	parser = argparse.ArgumentParser(description="Fast MD5 hash sort + dedup")
	parser.add_argument("input", help="Input file to sort in-place")
	parser.add_argument("--chunk",   type=int, default=CHUNK_SIZE,
						help="Lines per chunk (default: %d)" % CHUNK_SIZE)
	parser.add_argument("--workers", type=int, default=NUM_WORKERS,
						help="Parallel processes (default: all cores = %d)" % NUM_WORKERS)
	parser.add_argument("--tmp-dir", default=TEMP_DIR)
	args = parser.parse_args()

	if not os.path.exists(args.input):
		print("Error: file '%s' not found." % args.input, file=sys.stderr)
		sys.exit(1)

	input_size = os.path.getsize(args.input) / (1024.0 ** 3)
	tmp_output = args.input + ".sorting.tmp"
	log("=" * 55)
	log("Input  : %s  (%.2f GB)" % (args.input, input_size))
	log("Chunk  : %d lines  |  Workers: %d processes" % (args.chunk, args.workers))
	log("=" * 55)

	with tempfile.TemporaryDirectory(dir=args.tmp_dir) as tmp_dir:
		tmp_files = split_and_sort(
			args.input, tmp_dir, args.chunk, args.workers)
		total = merge_sorted_files(tmp_files, tmp_output, tmp_dir)

	output_size = os.path.getsize(tmp_output) / (1024.0 ** 3)
	os.replace(tmp_output, args.input)
	total_time = time.time() - _t0
	log("=" * 55)
	log("Done!  Unique hashes : %d" % total)
	log("	   Output size   : %.2f GB" % output_size)
	log("	   Total time	: %.1f s\a" % total_time)
	log("=" * 55)


if __name__ == "__main__":
	main()
