#!/usr/bin/env python3

# bech32

import hashlib
from ecdsa import SECP256k1, SigningKey
import bech32

from tqdm.contrib.concurrent import process_map

def hex_to_bytes(hex_str):
	return bytes.fromhex(hex_str)

def sha256(b):
	return hashlib.sha256(b).digest()

def tweak_pubkey(pubkey_bytes):
	tweak = sha256(pubkey_bytes)
	tweak_int = int.from_bytes(tweak, "big")
	tweaked_pubkey = (SECP256k1.generator * tweak_int).to_bytes("compressed")
	return tweaked_pubkey

def encode_bech32m(pubkey_bytes):
	witness_version = 0x01
	# Convert the bytes to a 5-bit representation
	pubkey_5bit = bech32.convertbits(pubkey_bytes, 8, 5, True)
	return bech32.bech32_encode("bc", [witness_version] + pubkey_5bit)

def private_key_to_taproot_address(private_key_hex):
	private_key_bytes = hex_to_bytes(private_key_hex)
	sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
	# Get the corresponding public key
	pubkey = sk.get_verifying_key().to_string("compressed")
	# Tweak the public key
	tweaked_pubkey = tweak_pubkey(pubkey)
	# Encode the tweaked public key as a bech32m address
	taproot_address = encode_bech32m(tweaked_pubkey)
	return taproot_address

print('Reading...', flush=True)
i=open('input.txt','r').read().splitlines()
print('Writing...', flush=True)
o=open('output.txt','w')

def go(pvk):
	try:
		taproot_address = private_key_to_taproot_address(pvk)
	except:
		return
	o.write(pvk+'\t'+taproot_address+'\n')
	o.flush()

process_map(go, i, max_workers=12, chunksize=1000)

import sys
print('\a',end='',file=sys.stderr)
