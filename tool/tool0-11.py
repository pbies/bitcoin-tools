#!/usr/bin/env python3

import base58
import binascii
import ecdsa
import ecdsa.der
import ecdsa.util
import hashlib
import math
import random
import re
import struct
import unittest
from subprocess import check_output
from tqdm import tqdm

def bw2wif1(s):
	sha=hashlib.sha256(s.encode()).digest()
	tmp=b'\x80'+sha
	return base58.b58encode_check(tmp).decode()

def bw2wifmany(i,o):
	f1=open(i,'r')
	f2=open(o,'w')
	cnt=sum(1 for line in open(i))
	for line in tqdm(f1, total=cnt, unit=" lines"):
		x=line.rstrip('\n').encode()
		sha=hashlib.sha256(x).digest()
		tmp=b'\x80'+sha
		h=base58.b58encode_check(tmp)
		i=h+b" 0 # "+x+b'\n'
		f2.write(i.decode())
	return

while True:
	print('Tool for cc v0.11 (C) 2023 Aftermath @Tzeeck')
	print('1. convert brainwallet to WIF - single')
	print('2. convert brainwallet to WIF - many (a file)')
	m=input('Choose number or empty to quit: ')

	match m:
		case '1':
			a=input('Enter brainwallet: ')
			print('WIF: '+bw2wif1(a)+'\n')
		case '2':
			a=input('Enter input filename [input.txt]: ')
			b=input('Enter output filename [output.txt]: ')
			if a=='':
				a='input.txt'
			if b=='':
				b='output.txt'
			bw2wifmany(a,b)
			print('Done!\n')
		case '':
			exit(0)
