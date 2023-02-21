#!/usr/bin/env python3

# decode many base58check; progress bar

from subprocess import check_output
from tqdm import tqdm

outfile = open("output.txt","w")

cnt=sum(1 for line in open("input.txt", 'r'))

with open("input.txt","r") as f:
	for line in tqdm(f, total=cnt, unit=" lines"):
		x=line.rstrip('\n')
		outfile.write(x[2:]+'\n')

outfile.close()
