#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.const import PUBLIC_KEY_TYPES
from hdwallet.cryptocurrencies import Bitcoin as Cryptocurrency
from hdwallet.hds import BIP84HD
from hdwallet.mnemonics import BIP39_MNEMONIC_LANGUAGES
from multiprocessing import Pool
from tqdm import tqdm
import sys, hashlib, base58
from hdwallet.entropies import (
	BIP39Entropy, BIP39_ENTROPY_STRENGTHS
)

words=open('english.txt','r').read().splitlines()

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def go(i):
	j=hex(i).encode()[2:]
	random_bytes=hashlib.sha256(j).digest()[0:32]

	try:
		hdwallet: HDWallet = HDWallet(
			cryptocurrency=Cryptocurrency,
			hd=BIP84HD,
			network=Cryptocurrency.NETWORKS.MAINNET,
			language=BIP39_MNEMONIC_LANGUAGES.ENGLISH,
			public_key_type=PUBLIC_KEY_TYPES.COMPRESSED,
			passphrase=None
		).from_entropy(
			entropy=BIP39Entropy(entropy=random_bytes)
		)
	except:
		return
	wif=pvk_to_wif2(hdwallet.private_key())
	r=f'{wif}\n{hdwallet.wif()}\n{hdwallet.address("P2PKH")}\n{hdwallet.address("P2SH")}\n{hdwallet.address("P2TR")}\n{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'
	#r=f'{wif}\n{hdwallet.wif()}\n\n'
	outfile.write(r)
	outfile.flush()

outfile = open('output.txt','w')

if __name__ == "__main__":
	max_ = 2**32
	i=0
	with Pool(processes=24) as p, tqdm(total=max_) as pbar:
		for result in p.imap(go, range(0, max_)):
			if i%1000==0:
				pbar.update(1000)
				pbar.refresh()
			i=i+1

	print('\a', end='', file=sys.stderr)
