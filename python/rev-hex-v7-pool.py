#!/usr/bin/env python3

import os, sys
from multiprocessing import Pool
from tqdm import tqdm

def go(line):
	line = line.rstrip(b'\n').decode()
	try:
		h2 = bytes.fromhex(line)[::-1].hex()
	except:
		return None
	h1 = line[::-1]
	tmp1, tmp2 = line[0::2], line[1::2]
	h3 = f'{tmp1}{tmp2}'
	h4 = f'{tmp2}{tmp1}'
	return f'{line}\n{h1}\n{h2}\n{h3}\n{h4}\n'

def main():
	th = 24
	chunksize = 10000
	infile = 'input.txt'
	outfile = 'output.txt'
	size = os.path.getsize(infile)

	with open(infile, 'rb') as f:
		lines = f.readlines()

	with Pool(th) as pool:
		with tqdm(total=len(lines), unit='lines') as pbar:
			results = []
			for chunk in pool.imap_unordered(go, lines, chunksize=chunksize):
				if chunk:
					results.append(chunk)
				pbar.update(1)

	with open(outfile, 'w') as f:
		f.writelines(results)

	print('\a', end='', file=sys.stderr)

if __name__ == "__main__":
	main()
