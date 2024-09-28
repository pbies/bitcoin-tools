#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
from tqdm import tqdm
import sys, hashlib, base58

hdwallet = HDWallet(symbol=BTC)

def sha(x):
	t1=hashlib.sha256()
	t1.update(x)
	return t1.digest()

def shahex(x):
	t1=hashlib.sha256()
	t1.update(x)
	return t1.hexdigest()

def pvk_to_wif2(key_hex):
	b=bytes.fromhex(key_hex)
	t1=b'\x80'+b
	w=base58.b58encode_check(t1)
	return w

def go(k):
	s=shahex(k)
	d1=s[0:32]
	d2=s[32:64]
	hdwallet.from_entropy(entropy=d1)
	pvk=hdwallet.private_key()
	wif=pvk_to_wif2(pvk).decode()
	outfile.write(wif+'\n')
	outfile.write(hdwallet.wif()+'\n')
	outfile.write(hdwallet.p2pkh_address()+'\n')
	outfile.write(hdwallet.p2sh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_in_p2sh_address()+'\n')
	outfile.write(hdwallet.p2wsh_address()+'\n')
	outfile.write(hdwallet.p2wsh_in_p2sh_address()+'\n\n')
	hdwallet.from_entropy(entropy=d2)
	pvk=hdwallet.private_key()
	wif=pvk_to_wif2(pvk).decode()
	outfile.write(wif+'\n')
	outfile.write(hdwallet.wif()+'\n')
	outfile.write(hdwallet.p2pkh_address()+'\n')
	outfile.write(hdwallet.p2sh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_in_p2sh_address()+'\n')
	outfile.write(hdwallet.p2wsh_address()+'\n')
	outfile.write(hdwallet.p2wsh_in_p2sh_address()+'\n\n')
	outfile.flush()

print('Reading...', flush=True)
infile = open('input.txt','rb')
lines = infile.read().splitlines()

print('Writing...', flush=True)
outfile = open('output.txt','w')
process_map(go, lines, max_workers=12, chunksize=1000)
#for i in tqdm(lines):
#	go(i)

print('\a',end='',file=sys.stderr)
