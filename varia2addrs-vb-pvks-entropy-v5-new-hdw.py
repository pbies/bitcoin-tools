#!/usr/bin/env python3

from ecdsa import SigningKey, SECP256k1
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Bitcoin as BTC
from hdwallet.hds import BIP32HD
from hdwallet.mnemonics import BIP39Mnemonic
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58
import os, sys, hashlib

hdwallet = HDWallet(cryptocurrency=BTC, hd=BIP32HD)

def pvk_to_wif(key_bytes):
	return base58.b58encode_check(b'\x80' + key_bytes)

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

def entropy_to_pvk(e):
	entropy_int = int(e, 16)
	order = SECP256k1.order
	if entropy_int >= order:
		return None
	private_key = SigningKey.from_secret_exponent(entropy_int, curve=SECP256k1)
	private_key_bytes = private_key.to_string()
	return private_key_bytes.hex()

def go(k):
	p1=entropy_to_pvk(k[0:32])
	p2=entropy_to_pvk(k[32:64])
	q1=pvk_to_wif2(p1)
	q2=pvk_to_wif2(p2)
	r=''
	r+=q1+'\n'
	hdwallet.from_private_key(p1)
	r+=hdwallet.wif()+'\n'
	r+=hdwallet.address("P2PKH")+'\n'
	r+=hdwallet.address("P2SH")+'\n'
	r+=hdwallet.address("P2TR")+'\n'
	r+=hdwallet.address("P2WPKH")+'\n'
	r+=hdwallet.address("P2WPKH-In-P2SH")+'\n'
	r+=hdwallet.address("P2WSH")+'\n'
	r+=hdwallet.address("P2WSH-In-P2SH")+'\n\n'
	hdwallet.from_private_key(p2)
	r+=q2+'\n'
	r+=hdwallet.wif()+'\n'
	r+=hdwallet.address("P2PKH")+'\n'
	r+=hdwallet.address("P2SH")+'\n'
	r+=hdwallet.address("P2TR")+'\n'
	r+=hdwallet.address("P2WPKH")+'\n'
	r+=hdwallet.address("P2WPKH-In-P2SH")+'\n'
	r+=hdwallet.address("P2WSH")+'\n'
	r+=hdwallet.address("P2WSH-In-P2SH")+'\n\n'
	outfile.write(r)
	outfile.flush()

infile = open('input.txt','r')
outfile = open('output.txt','w')

lines = infile.read().splitlines()

process_map(go, lines, max_workers=16, chunksize=1000)

print('\a', end='', file=sys.stderr)
