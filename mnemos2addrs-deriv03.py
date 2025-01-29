#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.derivations import IDerivation
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from mnemonic import Mnemonic
from multiprocessing import Pool
from tqdm import tqdm
import concurrent.futures
import sys

mnemo = Mnemonic("english")
o=open('output.txt','w')

def go(mnemo):
	hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)
	try:
		hdwallet.from_mnemonic(mnemonic=BIP39Mnemonic(mnemonic=mnemo))
	except:
		return

	for i in range(1, 320):
		o.write(mnemo+f' : {i}\n')

		derivation_path = "m/84'/0'/0'/0/"+str(i)
		hdwallet.from_derivation(IDerivation(derivation_path))

		adrs = [
			"P2PKH", "P2SH", "P2TR", "P2WPKH", "P2WPKH-In-P2SH", "P2WSH", "P2WSH-In-P2SH"
		]

		for adr in adrs:
			o.write(hdwallet.address(adr)+'\n')

		o.write('\n')
		o.flush()

th = 4
cnt=100

print('Reading...', flush=True)
mnemos=open('input.txt','r').read().splitlines()
print('Writing...', flush=True)
max_=len(mnemos)

c=0
with Pool(processes=th) as p, tqdm(total=max_) as pbar:
	for result in p.imap(go, mnemos):
		if c%cnt==0:
			pbar.update(cnt)
			pbar.refresh()
		c=c+1

print('\a', end='', file=sys.stderr)
