#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
from tqdm import tqdm
import sys
import base58

hdwallet = HDWallet(symbol=BTC)

outfile = open('wifs-output.txt','a')

def go(k):
	try:
		k=base58.b58decode_check(k)[0:].hex()[2:]
		hdwallet.from_private_key(private_key=k)
	except:
		return
	outfile.write(hdwallet.wif()+'\n')
	outfile.write(hdwallet.p2pkh_address()+'\n')
	outfile.write(hdwallet.p2sh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_in_p2sh_address()+'\n')
	outfile.write(hdwallet.p2wsh_address()+'\n')
	outfile.write(hdwallet.p2wsh_in_p2sh_address()+'\n\n')
	outfile.flush()

def main():
	print('Reading...', flush=True)
	infile = open('wifs.txt','r')
	lines = infile.read().splitlines()

	print('Writing...', flush=True)
	process_map(go, lines, max_workers=8, chunksize=1000)

	print('\a',end='',file=sys.stderr)

if __name__ == '__main__':
    main()