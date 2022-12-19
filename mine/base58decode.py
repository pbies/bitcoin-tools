#!/usr/bin/env python3

from subprocess import check_output
from tqdm import tqdm
import base58
import hashlib

outfile = open("output.txt","wb")

cnt=int(check_output(["wc", "-l", "input.txt"]).split()[0])

with open("input.txt","rb") as f:
	for line in tqdm(f, total=cnt, unit=" lines"):
		x=line.rstrip(b'\n')
		h=base58.b58decode_check(x)
		outfile.write(h+b'\n')

outfile.close()
