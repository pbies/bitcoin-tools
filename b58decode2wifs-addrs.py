#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from numba import cuda
from subprocess import check_output
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import hashlib
import multiprocessing
import sys

hdwallet = HDWallet(symbol=BTC)

print('Reading...')
i = open('input.txt','r').read().splitlines()
o = open("output.txt","w")

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(x):
	try:
		y=base58.b58decode_check(x)
	except:
		return
	z=b'\x00'*(32-len(y))+y
	z=z.hex()
	try:
		hdwallet.from_private_key(private_key=z)
	except:
		return
	wif=pvk_to_wif2(z)
	o.write(wif+'\n')
	o.write(hdwallet.wif()+'\n')
	o.write(hdwallet.p2pkh_address()+'\n')
	o.write(hdwallet.p2sh_address()+'\n')
	o.write(hdwallet.p2wpkh_address()+'\n')
	o.write(hdwallet.p2wpkh_in_p2sh_address()+'\n')
	o.write(hdwallet.p2wsh_address()+'\n')
	o.write(hdwallet.p2wsh_in_p2sh_address()+'\n\n')
	o.flush()

print('Writing...')
process_map(go, i, max_workers=20, chunksize=10000)

o.close()

print('Done!\a', file=sys.stderr)
