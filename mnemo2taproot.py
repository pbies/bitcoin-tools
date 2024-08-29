#!/usr/bin/env python3

# pip install mnemonic bip32utils ecdsa bech32 bip_utils

from bip_utils import Bip39SeedGenerator, Bip44, Bip86Coins, Bip86, Bip44Changes
from bip_utils import Bech32Encoder, CoinsConf
from ecdsa import SECP256k1, SigningKey
import hashlib
import bech32
from mnemonic import Mnemonic
from bip32utils import BIP32Key
import hmac
import binascii
from tqdm.contrib.concurrent import process_map

BIP32KEY_HARDEN = 0x80000000

def mnemonic_to_seed(mnemonic, passphrase=""):
	mnemonic = mnemonic.strip()
	passphrase = "mnemonic" + passphrase
	seed = hashlib.pbkdf2_hmac('sha512', mnemonic.encode('utf-8'), passphrase.encode('utf-8'), 2048)
	return seed

def sha256(b):
	return hashlib.sha256(b).digest()

def sha256(b):
	return hashlib.sha256(b).digest()

def tweak_pubkey(pubkey_bytes):
	tweak = sha256(pubkey_bytes)
	tweak_int = int.from_bytes(tweak, "big")
	tweaked_pubkey = (SECP256k1.generator * tweak_int).to_bytes("compressed")
	return tweaked_pubkey

def encode_bech32m(pubkey_bytes):
	witness_version = 0x01
	pubkey_5bit = bech32.convertbits(pubkey_bytes, 8, 5, True)
	return bech32.bech32_encode("bc", [witness_version] + pubkey_5bit)

def derive_taproot_address_from_mnemonic(mnemonic, passphrase=""):
	# Generate seed from mnemonic
	seed_bytes = Bip39SeedGenerator(mnemonic).Generate(passphrase)

	# Use BIP-86 to derive the key (m/86'/0'/0'/0/0)
	bip86_mst_ctx = Bip86.FromSeed(seed_bytes, Bip86Coins.BITCOIN)
	bip86_acc_ctx = bip86_mst_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)

	# Get the private key
	private_key = bip86_acc_ctx.PrivateKey().Raw().ToBytes()

	# Generate the public key using the Schnorr signature (BIP-340) method
	sk = SigningKey.from_string(private_key, curve=SECP256k1)
	pubkey = sk.get_verifying_key().to_string("compressed")

	# Tweak the public key for Taproot
	tweaked_pubkey = tweak_pubkey(pubkey)

	# Encode the tweaked public key as a Bech32m address
	taproot_address = encode_bech32m(tweaked_pubkey)

	return taproot_address

print('Reading...')
i=open('input.txt','r').read().splitlines()
print('Writing...')
o=open('output.txt','w')

def go(m):
	try:
		taproot_address = derive_taproot_address_from_mnemonic(m)
	except:
		return
	o.write(m+'\t'+taproot_address+'\n')
	o.flush()

process_map(go, i, max_workers=12, chunksize=1000)

import sys
print('\a',end='',file=sys.stderr)
