#!/usr/bin/env python3

from subprocess import check_output
from tqdm import tqdm
import base58
import hashlib

outfile = open("output.txt","w")

cnt=sum(1 for line in open("input.txt", 'r'))

with open("input.txt","r") as f:
	for line in tqdm(f, total=cnt, unit=" lines"):
		x=line.rstrip('\n')
		x=x[0:64]
		outfile.write(x+'\n')

outfile.close()
