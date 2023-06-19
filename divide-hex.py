#!/usr/bin/env python3

from tqdm import tqdm

o32 = open("32-addr.txt","w")
o40 = open("40-hash160.txt","w")
o64 = open("64-privkey.txt","w")
o128 = open("128-seed.txt","w")

cnt=sum(1 for line in open("input.txt", 'r'))

with open("input.txt","r") as f:
	for line in tqdm(f, total=cnt):
		x=line.strip()
		if len(x)==32:
			o32.write(x+'\n')
		if len(x)==40:
			o40.write(x+'\n')
		if len(x)==64:
			o64.write(x+'\n')
		if len(x)==128:
			o128.write(x+'\n')
