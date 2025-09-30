#!/usr/bin/env python3
import ecdsa
import hashlib
import base58
from subprocess import check_output
from tqdm import tqdm

# input: priv key base58_check
# output: pub addr base58_check

outfile = open("output.txt","wb")

cnt=sum(1 for line in open("input.txt", 'r'))

with open("input.txt","rb") as f:
	for line in tqdm(f, total=cnt, unit=" lines"):
		line=line.rstrip(b'\n')
		# WIF to private key by https://en.bitcoin.it/wiki/Wallet_import_format
		Private_key = base58.b58decode_check(line) 
		Private_key = Private_key[1:]

		# Private key to public key (ecdsa transformation)
		signing_key = ecdsa.SigningKey.from_string(Private_key, curve = ecdsa.SECP256k1)
		verifying_key = signing_key.get_verifying_key()
		public_key = bytes.fromhex("04") + verifying_key.to_string()

		# hash sha 256 of pubkey
		sha256_1 = hashlib.sha256(public_key)

		# hash ripemd of sha of pubkey
		ripemd160 = hashlib.new("ripemd160")
		ripemd160.update(sha256_1.digest())

		# checksum
		hashed_public_key = bytes.fromhex("00") + ripemd160.digest()
		checksum_full = hashlib.sha256(hashlib.sha256(hashed_public_key).digest()).digest()
		checksum = checksum_full[:4]
		bin_addr = hashed_public_key + checksum

		# encode address to base58 and print
		result_address = base58.b58encode(bin_addr)
		outfile.write(result_address+b"\n")
