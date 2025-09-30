#!/usr/bin/env python3

from tqdm import tqdm
import base58
import hashlib
import os

o=open('wifs.txt','wb')
for i in tqdm(range(10000000)):
	o.write(base58.b58encode_check(b'\x80'+hashlib.sha256(os.urandom(32)).digest())+b'\n')
