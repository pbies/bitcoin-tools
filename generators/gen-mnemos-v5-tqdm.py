#!/usr/bin/env python3

from tqdm import tqdm
import mnemonic
import sys

if __name__ == '__main__':
	f = open('mnemos.txt', 'a')
	mobj = mnemonic.Mnemonic("english")
	for i in tqdm(range(0, int(sys.argv[1]))):
		mnemonic_words = mobj.generate(strength=128)
		f.write(f'{mnemonic_words}\n')
		f.flush()
	print('\a', end='', file=sys.stderr)
