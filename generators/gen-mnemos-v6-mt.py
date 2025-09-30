#!/usr/bin/env python3

from multiprocessing import Pool
from tqdm import tqdm
import mnemonic
import sys

def go(k):
	mnemonic_words = mobj.generate(strength=128)
	f.write(f'{mnemonic_words}\n')

if __name__ == '__main__':
	count=range(0, int(sys.argv[1]))
	th=8
	max_=len(count)
	progress=2000

	f = open('mnemos.txt', 'a')
	mobj = mnemonic.Mnemonic("english")

	i=0
	with Pool(processes=th) as p, tqdm(total=max_) as pbar:
		for result in p.imap_unordered(go, count, chunksize=1000):
			if i%progress==0:
				pbar.update(progress)
				pbar.refresh()
				f.flush()
			i=i+1
	print('\a', end='', file=sys.stderr)
