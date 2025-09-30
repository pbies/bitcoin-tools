#!/usr/bin/env python3

# https://medium.com/@kootsZhin/step-by-step-guide-to-getting-bitcoin-address-from-private-key-in-python-7ec15072b71b
import hashlib
import base58
import codecs
import ecdsa
private_key = "18e14a7b6a307f426a94f8114701e7c8e774e7f9a47e2c2035db29a206321725"
private_key_bytes = bytes.fromhex(private_key)
# Generating a public key in bytes using SECP256k1 & ecdsa library
public_key_raw = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1).verifying_key
public_key_bytes = public_key_raw.to_string()
# Hex encoding the public key from bytes
public_key_hex = codecs.encode(public_key_bytes, 'hex')
# Bitcoin public key begins with bytes 0x04 so we have to add the bytes at the start
public_key = (b'04' + public_key_hex).decode("utf-8")
public_key

if (ord(bytearray.fromhex(public_key[-2:])) % 2 == 0):
	public_key_compressed = '02'
else:
	public_key_compressed = '03'
	
# Add bytes 0x02 to the X of the key if even or 0x03 if odd
public_key_compressed += public_key[2:66]
print(public_key_compressed)

# Converting to bytearray for SHA-256 hashing
hex_str = bytearray.fromhex(public_key_compressed)
sha = hashlib.sha256()
sha.update(hex_str)
print(sha.hexdigest()) # .hexdigest() is hex ASCII

rip = hashlib.new('ripemd160')
rip.update(sha.digest())
key_hash = rip.hexdigest()
print(key_hash) # Hash160

modified_key_hash = "00" + key_hash
print(modified_key_hash)

sha = hashlib.sha256()
hex_str = bytearray.fromhex(modified_key_hash)
sha.update(hex_str)
print(sha.hexdigest())

sha_2 = hashlib.sha256()
sha_2.update(sha.digest())
print(sha_2.hexdigest())

checksum = sha_2.hexdigest()[:8]
print(checksum)

byte_25_address = modified_key_hash + checksum
print(byte_25_address)

address = base58.b58encode(bytes(bytearray.fromhex(byte_25_address))).decode('utf-8')
print(address)
