#!/usr/bin/env python3
import bitcoin
from tqdm import tqdm

with open("input.txt","r") as f:
	content = f.readlines()

content = [x.strip() for x in content]
f.close()

outfile = open("output.txt","w")
for x in tqdm(content, total=len(content), unit="keys"):
	try:
		outfile.write(bitcoin.encode_privkey(x,'wif')+" 0\n")
	except:
		continue
#	outfile.write(bitcoin.encode_privkey(x,'wif_compressed')+"\n")

outfile.close()
