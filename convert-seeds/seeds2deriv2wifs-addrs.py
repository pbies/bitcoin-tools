#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.derivations import CHANGES
from hdwallet.derivations import DERIVATIONS
from hdwallet.derivations.bip84 import BIP84Derivation
from hdwallet.derivations.custom import CustomDerivation
from hdwallet.entropies import BIP39Entropy
from hdwallet.hds import BIP84HD
from hdwallet.mnemonics import BIP39Mnemonic
from hdwallet.seeds import BIP39Seed
from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import sys, os

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(k):
	hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP84HD).from_seed(seed=BIP39Seed(k))

	for l in range(0, 4):
		for m in range(0, 4):
			bip84_derivation = BIP84Derivation()
			bip84_derivation.from_coin_type(coin_type=BTC.COIN_TYPE)
			bip84_derivation.from_account(account=l)
			bip84_derivation.from_change(change=CHANGES.EXTERNAL_CHAIN)
			bip84_derivation.from_address(address=m)
			hdwallet.from_derivation(derivation=bip84_derivation)

			wif = pvk_to_wif2(hdwallet.private_key())
			r = (
				f'{wif}\n'
				f'{hdwallet.wif()}\n'
				f'{hdwallet.address("P2PKH")}\n'
				f'{hdwallet.address("P2SH")}\n'
				f'{hdwallet.address("P2TR")}\n'
				f'{hdwallet.address("P2WPKH")}\n'
				f'{hdwallet.address("P2WPKH-In-P2SH")}\n'
				f'{hdwallet.address("P2WSH")}\n'
				f'{hdwallet.address("P2WSH-In-P2SH")}\n\n'
			)
			outfile.write(r)
			outfile.flush()

infile = open('input.txt','r')
outfile = open('output.txt','w')

if __name__=='__main__':
	os.system('cls' if os.name == 'nt' else 'clear')
	print('Reading...', flush=True)
	lines = infile.read().splitlines()
	#lines = [x.strip() for x in lines]

	th=16
	max_=len(lines)

	print('Writing...', flush=True)
	i=0
	with Pool(processes=th) as p, tqdm(total=max_) as pbar:
		for result in p.imap_unordered(go, lines, chunksize=1024):
			if i%200==0:
				pbar.update(200)
				pbar.refresh()
			i=i+1

	print('\a', end='', file=sys.stderr)
