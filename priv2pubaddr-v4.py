#!/usr/bin/env python3
from subprocess import check_output
from tqdm import tqdm
from bitcoin import *

# input: priv key base58_check
# output: pub addr base58_check

outfile = open("output.txt","w")

cnt=int(check_output(["wc", "-l", "input.txt"]).split()[0])

with open("input.txt","r") as f:
	for line in tqdm(f, total=cnt, unit=" lines"):
		line=line.rstrip('\n')

		pubaddr = privtoaddr(line)
		outfile.write(pubaddr+"\n")
