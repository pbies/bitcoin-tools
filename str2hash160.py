#!/usr/bin/env python3

from cryptos import *
from subprocess import check_output
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import hashlib

def HASH160(t):
	return hashlib.new('ripemd160', hashlib.sha256(t).digest() ).hexdigest()

cnt=sum(1 for line in open("input.txt", 'rb'))

i = open("input.txt","rb")
o = open("output.txt","w")

for l in tqdm(i,total=cnt):
	l=l.rstrip(b'\n')
	h=HASH160(l)
	o.write(h)
	o.write('\n')
	o.flush()
