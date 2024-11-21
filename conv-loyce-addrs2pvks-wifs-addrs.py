#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
from tqdm import tqdm
import sys, base58

hdwallet = HDWallet(symbol=BTC)

def pvk_to_wif2(key_hex): # in: '0000... [64] out: b'5HpH...
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(k):
	try:
		a=base58.b58decode_check(k)
	except:
		print(f'Error with: {k}')
		return

	b=a.hex()
	c='0'*(64-len(b))+b
	d=b+'0'*(64-len(b))

	try:
		hdwallet.from_private_key(private_key=c)
	except:
		return
	wif=pvk_to_wif2(c)
	s1=wif+'\n'+hdwallet.wif()+'\n'+hdwallet.p2pkh_address()+'\n'+hdwallet.p2sh_address()+'\n'+hdwallet.p2wpkh_address()+'\n'+hdwallet.p2wpkh_in_p2sh_address()+'\n'+hdwallet.p2wsh_address()+'\n'+hdwallet.p2wsh_in_p2sh_address()+'\n\n'

	try:
		hdwallet.from_private_key(private_key=d)
	except:
		return
	wif=pvk_to_wif2(d)
	s2=wif+'\n'+hdwallet.wif()+'\n'+hdwallet.p2pkh_address()+'\n'+hdwallet.p2sh_address()+'\n'+hdwallet.p2wpkh_address()+'\n'+hdwallet.p2wpkh_in_p2sh_address()+'\n'+hdwallet.p2wsh_address()+'\n'+hdwallet.p2wsh_in_p2sh_address()+'\n\n'

	outfile.write(s1)
	outfile.write(s2)
	outfile.flush()

print('Reading...', flush=True)
infile = open('input.txt','r')
lines = infile.read().splitlines()

print('Writing...', flush=True)
outfile = open('output.txt','w')
process_map(go, lines, max_workers=24, chunksize=10000)

print('\a',end='',file=sys.stderr)
