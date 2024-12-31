#!/usr/bin/env python3

from ecdsa import SigningKey, SECP256k1
from hashlib import sha256
from hdwallet import HDWallet
from hdwallet.const import PUBLIC_KEY_TYPES
from hdwallet.cryptocurrencies import Bitcoin as Cryptocurrency
from hdwallet.hds import BIP84HD
from hdwallet.mnemonics import BIP39_MNEMONIC_LANGUAGES
from hdwallet.symbols import BTC
from multiprocessing import Pool
from random import randint
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import json
import secrets
import sys, hashlib, base58
import time
from hdwallet.mnemonics import BIP39Mnemonic
from hdwallet.entropies import (
	BIP39Entropy, BIP39_ENTROPY_STRENGTHS
)
from hdwallet.derivations import (
	BIP44Derivation, CHANGES
)

order = SECP256k1.order
word_number=12
size_ENT=128
size_CS=int(size_ENT/32)

words=open('english.txt','r').read().splitlines()

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def entropy_to_pvk(e):
	entropy_int = int(e, 16)
	if entropy_int >= order or entropy_int < 1:
		return None
	private_key = SigningKey.from_secret_exponent(entropy_int, curve=SECP256k1)
	private_key_bytes = private_key.to_string()
	return private_key_bytes.hex()

def go(i):
	j=hex(i).encode()[2:]
	random_bytes=hashlib.sha256(j).digest()[0:32]

	words_extracted=''

	n_bytes=int(size_ENT/8)
	random_bits = ''.join(['{:08b}'.format(b) for b in random_bytes])
	INITIAL_ENTROPY = random_bits[:size_ENT]

	encoded=INITIAL_ENTROPY.encode('utf-8')
	hash=random_bytes
	bhash=''.join(format(byte, '08b') for byte in hash)

	CS=bhash[:size_CS]

	FINAL_ENTROPY=INITIAL_ENTROPY+CS

	for t in range(word_number):
		extracted_bits=FINAL_ENTROPY[11*t:11*(t+1)]

		word_index=int(extracted_bits, 2)

		if t==0: words_extracted=	 words[word_index]
		else:	words_extracted+=' '+words[word_index]

	try:
		hdwallet: HDWallet = HDWallet(
			cryptocurrency=Cryptocurrency,
			hd=BIP84HD,
			network=Cryptocurrency.NETWORKS.MAINNET,
			language=BIP39_MNEMONIC_LANGUAGES.ENGLISH,
			public_key_type=PUBLIC_KEY_TYPES.COMPRESSED,
			passphrase=None
		).from_mnemonic(
			mnemonic=BIP39Mnemonic(mnemonic=words_extracted)
		)
	except:
		return
	wif=pvk_to_wif2(hdwallet.private_key())
	#r=f'{wif}\n{hdwallet.wif()}\n{hdwallet.address("P2PKH")}\n{hdwallet.address("P2SH")}\n{hdwallet.address("P2TR")}\n{hdwallet.address("P2WPKH")}\n{hdwallet.address("P2WPKH-In-P2SH")}\n{hdwallet.address("P2WSH")}\n{hdwallet.address("P2WSH-In-P2SH")}\n\n'
	r=f'{wif}\n{hdwallet.wif()}\n\n'
	outfile.write(r)
	outfile.flush()

def gen():
	for r in range(0, 2**32):
		yield r

outfile = open('output.txt','w')

if __name__ == "__main__":
	max_ = 2**32
	i=0
	with Pool(processes=16) as p, tqdm(total=max_) as pbar:
		for result in p.imap(go, range(0, max_)):
			if i%1000==0:
				pbar.update(1000)
				pbar.refresh()
			i=i+1

	print('\a', end='', file=sys.stderr)
