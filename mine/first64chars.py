#!/usr/bin/env python3

from subprocess import check_output
from tqdm import tqdm
import base58
import hashlib

outfile = open("output.txt","w")

cnt=int(check_output(["wc", "-l", "input.txt"]).split()[0])

with open("input.txt","r") as f:
	for line in tqdm(f, total=cnt, unit=" lines"):
		x=line.rstrip('\n')
		x=x[0:64]
		outfile.write(x+'\n')

outfile.close()
