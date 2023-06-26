#!/usr/bin/env python3

from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import hashlib
import os

o=open('wifs.txt','wb')

def go(x):
	o.write(base58.b58encode_check(b'\x80'+hashlib.sha256(os.urandom(32)).digest())+b'\n')
	o.flush()
	return

process_map(go, range(10000000), max_workers=4, chunksize=10000)
