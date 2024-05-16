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

# cnt=sum(1 for line in open("input.txt", 'rb'))

def go(x):
	pwd=x.rstrip(b'\n')
	sha=hashlib.sha256(pwd).digest()
	tmp=b'\x80'+sha
	wif=base58.b58encode_check(tmp)
	addr=privtoaddr(tmp)
	i=wif+b'\t'+str.encode(addr)+b'\n'
	o.write(i)
	o.flush()
	return

process_map(go, i.readlines(), max_workers=12, chunksize=10000)

import sys
print('\a',end='',file=sys.stderr)
