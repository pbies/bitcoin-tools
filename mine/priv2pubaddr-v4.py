#!/usr/bin/env python3
from subprocess import check_output
from tqdm import tqdm
from bitcoin import *

# input: priv key base58_check
# output: pub addr base58_check

outfile = open("output.txt","w")

cnt=sum(1 for line in open("input.txt", 'r'))

with open("input.txt","r") as f:
	for line in tqdm(f, total=cnt, unit=" lines"):
		line=line.rstrip('\n')

		pubaddr = privtoaddr(line)
		outfile.write(pubaddr+"\n")
