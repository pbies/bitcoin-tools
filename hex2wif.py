#!/usr/bin/env python3
import bitcoin

with open("input.txt","r") as f:
    content = f.readlines()

content = [x.strip() for x in content]
f.close()

outfile = open("output.txt","w")
for x in content:
    outfile.write(bitcoin.encode_privkey(x,'wif')+"\n")
#    outfile.write(bitcoin.encode_privkey(x,'wif_compressed')+"\n")

outfile.close()
