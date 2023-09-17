#!/usr/bin/env python3

# brainwallets to WIFs with progress and original text as comment; also address

from cryptos import *
from subprocess import check_output
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import hashlib

i = open("input.txt","rb")
o = open("output.txt","wb")

cnt=sum(1 for line in open("input.txt", 'r'))

def go(x):
	pwd=x.rstrip(b'\n')
	sha=hashlib.sha256(pwd).digest()
	tmp=b'\x80'+sha
	wif=base58.b58encode_check(tmp)
	pub=privtopub(tmp)
	addr=pubtoaddr(pub)
	i=wif+b' 0 # '+str.encode(addr)+b' '+bytearray(pwd)+b'\n'
	o.write(i)
	o.flush()
	return

process_map(go, i.readlines(), max_workers=4, chunksize=10000)
