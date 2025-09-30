#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm import tqdm
import base58
import sys
from tqdm.contrib.concurrent import process_map

hdwallet = HDWallet(symbol=BTC)

def go(k):
	k=k.strip()
	try:
		hdwallet.from_mnemonic(mnemonic=k)
	except:
		try:
			hdwallet.from_private_key(private_key=k)
		except:
			try:
				hdwallet.from_seed(seed=k)
			except:
				try:
					hdwallet.from_wif(wif=k)
				except:
					try:
						hdwallet.from_xprivate_key(xprivate_key=k)
					except:
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

infile = open('input.txt','r')
outfile = open('output.txt','w')

lines = infile.readlines()
lines = [x.strip() for x in lines]

process_map(go, lines, max_workers=12, chunksize=1000)

print('\a',end='',file=sys.stderr)
