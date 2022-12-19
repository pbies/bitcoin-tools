#!/usr/bin/env python3

import base58
import hashlib
import os
import sys
from random import randrange

def sha256(data):
	return hashlib.sha256(data).digest();

def b58(data):
	return base58.b58encode_check(data);

def to_wif(data):
	return b58(b'\x80'+sha256(data));

o=open("result.txt","wb")

for i in range(200000):
	k=randrange(65)
	l=os.urandom(k)
	o.write(to_wif(l)+b' 0\n')
