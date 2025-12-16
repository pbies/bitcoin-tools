#!/usr/bin/env python3

import os, sys
from multiprocessing import Pool
from tqdm import tqdm

def go(line):
	line = line.rstrip(b'\n').decode(errors='strict')
	try:
		h2 = bytes.fromhex(line)[::-1].hex()
	except Exception:
		return None
	h1 = line[::-1]
	tmp1, tmp2 = line[0::2], line[1::2]
	h3 = f'{tmp1}{tmp2}'
	h4 = f'{tmp2}{tmp1}'
	return f'{line}\n{h1}\n{h2}\n{h3}\n{h4}\n'

def line_iter(fh, pbar):
	for raw in fh:
		pbar.update(len(raw))
		yield raw

def main():
	th = 24
	chunksize = 10000
	infile = 'input.txt'
	outfile = 'output.txt'

	size = os.path.getsize(infile)

	with open(infile, 'rb') as fin, open(outfile, 'w', buffering=1) as fout:
		with tqdm(total=size, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
			with Pool(th) as pool:
				for out in pool.imap_unordered(go, line_iter(fin, pbar), chunksize=chunksize):
					if out:
						fout.write(out)

	print('\a', end='', file=sys.stderr)

if __name__ == "__main__":
	main()
