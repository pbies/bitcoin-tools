#!/usr/bin/env python3

# this program is bad written, don't use!

from bitcoin import *
from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm import tqdm

def str_to_hex(text):
	return binascii.hexlify(text.encode()).decode()

hdwallet = HDWallet(symbol=BTC)

infile = open('input.txt','r').read().splitlines()
cnt=len(infile)
outfile = open('output.txt','w')

for line in tqdm(infile, total=cnt):
	line=str_to_hex(line)
	line='0'*(64-len(line))+line

	hdwallet.from_private_key(private_key=line)
	outfile.write('pvk: ')
	outfile.write(line)
	outfile.write('\n')
	outfile.write('WIF: ')
	outfile.write(hdwallet.wif())
	outfile.write('\n')
	outfile.write('p2pkh: ')
	outfile.write(hdwallet.p2pkh_address()+'\n')
	outfile.write('p2sh: ')
	outfile.write(hdwallet.p2sh_address()+'\n')
	outfile.write('p2wpkh: ')
	outfile.write(hdwallet.p2wpkh_address()+'\n')
	outfile.write('p2wsh: ')
	outfile.write(hdwallet.p2wsh_address()+'\n\n')

	line='0'*(128-len(line))+line
	hdwallet.from_seed(seed=line)
	outfile.write('seed: ')
	outfile.write(line)
	outfile.write('\n')
	outfile.write('WIF: ')
	outfile.write(hdwallet.wif())
	outfile.write('\n')
	outfile.write('p2pkh: ')
	outfile.write(hdwallet.p2pkh_address()+'\n')
	outfile.write('p2sh: ')
	outfile.write(hdwallet.p2sh_address()+'\n')
	outfile.write('p2wpkh: ')
	outfile.write(hdwallet.p2wpkh_address()+'\n')
	outfile.write('p2wsh: ')
	outfile.write(hdwallet.p2wsh_address()+'\n\n')

import sys
print('\a',end='',file=sys.stderr)
