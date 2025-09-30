#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.derivations import IDerivation
from hdwallet.hds import BIP32HD, BIP44HD, BIP49HD, BIP84HD, BIP86HD, BIP141HD
from hdwallet.derivations.bip44 import BIP44Derivation
from hdwallet.derivations.bip84 import BIP84Derivation
from hdwallet.derivations.custom import CustomDerivation
from hdwallet.mnemonics import BIP39Mnemonic
from mnemonic import Mnemonic
from multiprocessing import Pool
from tqdm import tqdm
import concurrent.futures
import sys

mnemo = Mnemonic("english")
o=open('output84.txt','w')

def go(mnemo):
	for a in range(0,3):
		for b in range(0,3):
			#for c in range(0,3):
				#for i in range(0, 3):
			try:
				hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP84HD)
				hdwallet.from_mnemonic(mnemonic=BIP39Mnemonic(mnemonic=mnemo))
				derivation_path = f"m/84'/{str(a)}'/{str(b)}'/{str(c)}/0"
				bip84_derivation: BIP84Derivation = BIP84Derivation()
				bip84_derivation.from_coin_type(coin_type=a)
				bip84_derivation.from_account(account=b)
				bip84_derivation.from_change(change="external-chain")
				bip84_derivation.from_address(address=0)
				#print(bip84_derivation.path())
				o.write(f'{mnemo} : {derivation_path} : wif=')
				hdwallet.from_derivation(bip84_derivation)
				o.write(f'{hdwallet.wif()}\n')

				adrs = [
					"P2PKH", "P2SH", "P2TR", "P2WPKH", "P2WPKH-In-P2SH", "P2WSH", "P2WSH-In-P2SH"
				]

				for adr in adrs:
					o.write(hdwallet.address(adr)+'\n')
				o.write('\n')
			except:
				return

	o.flush()

th = 16
cnt = 10

print('Reading...', flush=True)
mnemos=set(open('input.txt','r').read().splitlines())
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
