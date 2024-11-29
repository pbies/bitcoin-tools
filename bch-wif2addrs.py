#!/usr/bin/env python3

from tqdm.contrib.concurrent import process_map
from tqdm import tqdm
import sys, base58
import bitcash

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(wif):
	try:
		pvk=bitcash.Key(wif)
	except:
		return
	adr=pvk.address
	a=wif+'\n'+pvk.to_hex()+'\n'+adr[12:]+'\n\n'
	outfile.write(a)
	outfile.flush()

print('Reading...', flush=True)
infile = open('input.txt','r')
lines = infile.read().splitlines()

print('Writing...', flush=True)
outfile = open('output.txt','w')
process_map(go, lines, max_workers=16, chunksize=1000)

print('\a',end='',file=sys.stderr)
