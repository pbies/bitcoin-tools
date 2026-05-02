#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import sys, base58, random
import itertools

def main():
	o = open('primes01.txt', 'w')

	x=0
	while True:
		a=(x*6)-1
		b=(x*6)+1
		if a%5!=0:
			o.write(f'{a}\n')
		if b%5!=0:
			o.write(f'{b}\n')
		if b>10_000_000_000:
			break
		x+=1

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
