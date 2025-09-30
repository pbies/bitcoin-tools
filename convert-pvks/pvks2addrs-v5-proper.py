#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
from tqdm import tqdm
import sys, base58

hdwallet = HDWallet(symbol=BTC)

def pvk_to_wif2(key_hex): # in: '0000... [64] out: b'5HpH...
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex))

def go(k):
	try:
		hdwallet.from_private_key(private_key=k)
	except:
		return
	wif=pvk_to_wif2(k).decode()
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
infile = open('input.txt','r')
lines = infile.read().splitlines()

print('Writing...', flush=True)
outfile = open('output.txt','w')
process_map(go, lines, max_workers=8, chunksize=1000)

print('\a',end='',file=sys.stderr)
