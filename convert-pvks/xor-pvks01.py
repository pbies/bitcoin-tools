#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from multiprocessing import Pool
from tqdm import tqdm
import sys, base58, os
import datetime, time

infile_path = 'input.txt'
outfile_path = 'output.txt'
num_processes = 24
hdwallet_bip32 = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
c=10000
d=10000
g=2**256
h=2**256-1
i=0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd036413f
j=0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364140
k=0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

def go(x):
	x=x.rstrip('\n')
	y=int(x,16)
	a=hex(g-y)[2:].zfill(64)
	b=hex(h-y)[2:].zfill(64)
	c=hex(i-y)[2:].zfill(64)
	d=hex(j-y)[2:].zfill(64)
	e=hex(k-y)[2:].zfill(64)
	w=f'{a}\n{b}\n{c}\n{d}\n{e}\n\n'
	with open(outfile_path, 'a') as outfile:
		outfile.write(w)

def main():
	os.system('cls' if os.name == 'nt' else 'clear')
	start_msg='Program started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(start_msg)
	start_time=time.time()

	open(outfile_path, 'w').close()
	print('Reading...', flush=True)
	infile=open(infile_path,'r').read().splitlines()
	print('Writing...', flush=True)
	t=0
	with Pool(processes=num_processes) as pool, tqdm(total=len(infile)) as pbar:
		for results in pool.imap_unordered(go, infile, chunksize=c):
			t+=1
			if t%d==0:
				pbar.update(d)
				pbar.refresh()

	stop_time=time.time()
	print(start_msg)
	print('Program stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {str(datetime.timedelta(seconds=stop_time-start_time))}')
	print('\a', end='', file=sys.stderr)

if __name__ == "__main__":
	main()
