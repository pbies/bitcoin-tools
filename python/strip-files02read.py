#!/usr/bin/env python3

import os
import glob
import sys
from tqdm import tqdm
from pathlib import Path

def _fast_count_lines2(file_path: str, bufsize: int = 1024 * 1024) -> int:
	cnt = 0
	with open(file_path, 'rb', buffering=bufsize) as f:
		while True:
			chunk = f.read(bufsize)
			if not chunk:
				break
			cnt += chunk.count(b'\n')
	try:
		if cnt == 0:
			with open(file_path, 'rb') as g:
				for _ in g:
					cnt += 1
			return cnt
		with open(file_path, 'rb') as g:
			g.seek(-1, os.SEEK_END)
			if g.read(1) != b'\n':
				cnt += 1
	except OSError:
		pass
	return cnt

def main():
	for path in glob.glob("*.txt"):
		print(path)
		cnt = _fast_count_lines2(path)
		with open(path, "rb") as f:
			with open(path + '.out', "wb") as g:
				for i in tqdm(range(cnt)):
					l = f.readline()
					if not l:  # End of file check
						break
					g.write(l.strip() + b"\n")

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
