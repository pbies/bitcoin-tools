#!/usr/bin/env python3

from cryptos import *
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import hashlib
from hdwallet import HDWallet
from hdwallet.symbols import BTC
from pprint import pprint

hdwallet = HDWallet(symbol=BTC)

infile=open("input.txt","r")
outfile = open("output.txt","w")

def worker(line):
	m=line.strip()
	try:
		hdwallet.from_mnemonic(mnemonic=m)
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
	process_map(worker, infile.readlines(), max_workers=10, chunksize=1000)

	infile.close()
	outfile.flush()
	outfile.close()

	import sys
	print('\a',end='',file=sys.stderr)

if __name__ == '__main__':
	main()
