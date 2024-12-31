#!/usr/bin/env python3

from ecdsa import SigningKey, SECP256k1
from hashlib import sha256
from hdwallet import HDWallet
from hdwallet.symbols import BTC
from multiprocessing import Pool
from random import randint
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import secrets
import sys, hashlib, base58
import time
from hdwallet import BIP84HDWallet

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
	#print('#'*20)
	j=hex(i).encode()[2:]
	#print(f'j = {j}')
	random_bytes=hashlib.sha256(j).digest()[0:32]
	#print(f'k = {k}')

	words_extracted=''

	n_bytes=int(size_ENT/8)
	random_bits = ''.join(['{:08b}'.format(b) for b in random_bytes])
	INITIAL_ENTROPY = random_bits[:size_ENT]
	#assert(len(INITIAL_ENTROPY)==size_ENT)

	encoded=INITIAL_ENTROPY.encode('utf-8')
	hash=random_bytes
	bhash=''.join(format(byte, '08b') for byte in hash)
	#assert(len(bhash)==256)

	#the first ENT / 32 bits of its SHA256 hash
	CS=bhash[:size_CS]

	#This checksum is appended to the end of the initial entropy.
	FINAL_ENTROPY=INITIAL_ENTROPY+CS
	#assert(len(FINAL_ENTROPY)==size_ENT+size_CS)

	for t in range(word_number):
		#split into groups of 11 bits, 
		extracted_bits=FINAL_ENTROPY[11*t:11*(t+1)]

		# each encoding a number from 0-2047,
		word_index=int(extracted_bits, 2)

		#serving as an index into a wordlist.
		if t==0: words_extracted=	 words[word_index]
		else:	words_extracted+=' '+words[word_index]

	#print(words_extracted)
	try:
		bip84_hdwallet: BIP84HDWallet = BIP84HDWallet(symbol=BTC, account=0, change=False, address=0)
		bip84_hdwallet.from_mnemonic(mnemonic=words_extracted)
	except:
		return
	w=pvk_to_wif2(bip84_hdwallet.private_key())
	r=w+'\n'
	r+=bip84_hdwallet.wif()+'\n'
	r+=bip84_hdwallet.address()+'\n\n'
	# r+=hdwallet.p2pkh_address()+'\n'
	# r+=hdwallet.p2sh_address()+'\n'
	# r+=hdwallet.p2wpkh_address()+'\n'
	# r+=hdwallet.p2wpkh_in_p2sh_address()+'\n'
	# r+=hdwallet.p2wsh_address()+'\n'
	# r+=hdwallet.p2wsh_in_p2sh_address()+'\n\n'
	outfile.write(r)
	outfile.flush()

def gen():
	for r in range(0, 2**32):
		yield r

outfile = open('output.txt','w')

if __name__ == "__main__":
	max_ = 2**32
	with Pool(processes=16) as p, tqdm(total=max_) as pbar:
		for result in p.imap(go, range(0, max_)):
			pbar.update()
			pbar.refresh()

	print('\a', end='', file=sys.stderr)
