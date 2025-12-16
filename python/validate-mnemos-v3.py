#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import sys
import time

hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

infile = open('mnemos.txt','r')
good = open('mnemos-good.txt','w')
bad = open('mnemos-bad.txt','w')

def go(k):
	try:
		hdwallet.from_mnemonic(mnemonic=BIP39Mnemonic(k))
	except:
		bad.write(k+'\n')
		#bad.flush()
		return
	good.write(hdwallet.mnemonic()+'\n')
	#good.flush()

print('Reading...', flush=True)
lines = infile.read().splitlines()
lines = [x.strip() for x in lines]

print('Writing...', flush=True)
process_map(go, lines, max_workers=24, chunksize=1000, ascii=False)

print('\a', end='', file=sys.stderr)
