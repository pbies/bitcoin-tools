#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import Optional, Iterable

def process_line(line: str) -> Optional[str]:
	line = line.strip()
	if not line:
		return None
	return None

def _worker_wrapper(line: str) -> Optional[str]:
	try:
		return process_line(line)
	except Exception:
		# Ignore individual line errors
		return None

def read_lines(file_path: Path, chunk_size: int = 10000) -> Iterable[list]:
	with file_path.open('r', encoding='utf-8', errors='replace') as f:
		while True:
			chunk = []
			for _ in range(chunk_size):
				l = f.readline()
				if not l:
					break
				chunk.append(l)
			if not chunk:
				break
			yield chunk

def write_results(results: Iterable[str], out_path: Path) -> None:
	if not results:
		return
	with out_path.open('a', encoding='utf-8') as f:
		for r in results:
			if r is not None:
				f.write(r)

def main():
	parser = argparse.ArgumentParser(description="Template: read lines -> process_line -> write output")
	parser.add_argument('-i','--input', required=True, help='input file path')
	parser.add_argument('-o','--output', required=True, help='output file path')
	parser.add_argument('-w','--workers', type=int, default=1, help='number of processes (1 = no multiprocessing)')
	parser.add_argument('-c','--chunk', type=int, default=10000, help='number of lines per chunk')
	args = parser.parse_args()

	in_path = Path(args.input)
	out_path = Path(args.output)

	if not in_path.exists():
		sys.exit(1)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	out_path.write_text('', encoding='utf-8')  # clear/create output file

	workers = max(1, args.workers)
	if workers > cpu_count():
		workers = cpu_count()

	if workers == 1:
		for chunk in read_lines(in_path, args.chunk):
			results = []
			for line in chunk:
				r = _worker_wrapper(line)
				if r is not None:
					results.append(r)
			write_results(results, out_path)
	else:
		with Pool(processes=workers) as pool:
			for chunk in read_lines(in_path, args.chunk):
				results = pool.map(_worker_wrapper, chunk)
				write_results(results, out_path)

if __name__ == '__main__':
	main()
