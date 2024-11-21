#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm import tqdm
import base58
import sys
from tqdm.contrib.concurrent import process_map

hdwallet = HDWallet(symbol=BTC)

def pvk_to_wif(key_bytes):
	return base58.b58encode_check(b'\x80' + key_bytes)

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex))

def go(k):
	try:
		hdwallet.from_entropy(entropy=k[0:32])
		tmp2=hdwallet
	except:
		tmp2=None
	try:
		hdwallet.from_entropy(entropy=k[32:64])
		tmp3=hdwallet
	except:
		tmp3=None

	for i in [tmp2, tmp3]:
		if i!=None:
			pvk=i.private_key()
			wif=pvk_to_wif2(pvk).decode()
			outfile.write(wif+'\n')
			outfile.write(i.wif()+'\n')
			outfile.write(i.p2pkh_address()+'\n')
			outfile.write(i.p2sh_address()+'\n')
			outfile.write(i.p2wpkh_address()+'\n')
			outfile.write(i.p2wpkh_in_p2sh_address()+'\n')
			outfile.write(i.p2wsh_address()+'\n')
			outfile.write(i.p2wsh_in_p2sh_address()+'\n\n')
			outfile.flush()

infile = open('input.txt','r')
outfile = open('output.txt','w')

lines = infile.read().splitlines()

process_map(go, lines, max_workers=24, chunksize=10000)

print('\a', end='', file=sys.stderr)
