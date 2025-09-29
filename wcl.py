#!/usr/bin/env python3

import os, sys

def _fast_count_lines(path: str, bufsize: int = 1024 * 1024) -> int:
	cnt = 0
	with open(path, 'rb', buffering=bufsize) as f:
		while True:
			chunk = f.read(bufsize)
			if not chunk:
				break
			cnt += chunk.count(b'\n')
	try:
		if cnt == 0:
			with open(path, 'rb') as g:
				for _ in g:
					cnt += 1
			return cnt
		with open(path, 'rb') as g:
			g.seek(-1, os.SEEK_END)
			if g.read(1) != b'\n':
				cnt += 1
	except OSError:
		pass
	return cnt

def main():
	print(_fast_count_lines(sys.argv[1]))
	print('\a', end='', file=sys.stderr)

if __name__=='__main__':
	main()
