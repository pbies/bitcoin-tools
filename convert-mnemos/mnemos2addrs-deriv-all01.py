#!/usr/bin/env python3

# don't use!

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.derivations import IDerivation
from hdwallet.hds import BIP32HD, BIP44HD, BIP49HD, BIP84HD, BIP86HD, BIP141HD
from hdwallet.mnemonics import BIP39Mnemonic
from mnemonic import Mnemonic
from multiprocessing import Pool
from tqdm import tqdm
import concurrent.futures
import sys

mnemo = Mnemonic("english")
o=open('output.txt','w')

def go(mnemo):
		for k in [BIP32HD, BIP44HD, BIP49HD, BIP84HD, BIP86HD, BIP141HD]:
			for j in [44, 49, 84, 86]:
				for i in range(0, 321):
					try:
						hdwallet = HDWallet(cryptocurrency=BTC, hd=k)
						hdwallet.from_mnemonic(mnemonic=BIP39Mnemonic(mnemonic=mnemo))
						derivation_path = "m/"+str(j)+"'/0'/0'/0/"+str(i)
						o.write(mnemo+f' : {k.__name__} : {derivation_path}\n')
						hdwallet.from_derivation(IDerivation(derivation_path))

						adrs = [
							"P2PKH", "P2SH", "P2TR", "P2WPKH", "P2WPKH-In-P2SH", "P2WSH", "P2WSH-In-P2SH"
						]

						for adr in adrs:
							o.write(hdwallet.address(adr)+'\n')
						o.write('\n')
					except:
						return

		o.flush()

th = 8
cnt = 1

print('Reading...', flush=True)
mnemos=open('input.txt','r').read().splitlines()
print('Writing...', flush=True)
max_=len(mnemos)

c=0
with Pool(processes=th) as p, tqdm(total=max_) as pbar:
	for result in p.imap_unordered(go, mnemos, chunksize=1000):
		if c%cnt==0:
			pbar.update(cnt)
			pbar.refresh()
		c=c+1

print('\a', end='', file=sys.stderr)
