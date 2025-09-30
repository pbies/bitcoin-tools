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
import requests
import struct
import unittest
from subprocess import check_output
from tqdm import tqdm
from os import system, name

def clear():
	if name == 'nt':
		_ = system('cls')
	else:
		_ = system('clear')
	return

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

def checkBTCbal(a):
	r=requests.get('https://blockchain.info/q/addressbalance/'+a)
	if not r.status_code==200:
		print('Error',r.status_code)
		exit()
	b=int(r.text)
	return b

clear()
while True:
	print('Tool for cc v0.12 (C) 2023 Aftermath @Tzeeck')
	print('1. convert brainwallet to WIF - single')
	print('2. convert brainwallet to WIF - many (a file)')
	print('3. check BTC balance - single')
	m=input('Enter number or empty to quit: ')

	match m:
		case '1':
			a=input('Enter brainwallet: ')
			print('\nWIF: '+bw2wif1(a)+'\n')
		case '2':
			a=input('Enter input filename [input.txt]: ')
			b=input('Enter output filename [output.txt]: ')
			if a=='':
				a='input.txt'
			if b=='':
				b='output.txt'
			bw2wifmany(a,b)
			print('Done!\n')
		case '3':
			a=input('Enter address: ')
			sat=checkBTCbal(a)
			print('\n',a,'\t',sat,'sat\t',sat/100000,'mBTC\t',sat/100000000,'BTC\n')
		case '':
			exit(0)
