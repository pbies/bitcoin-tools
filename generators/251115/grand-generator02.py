#!/usr/bin/env python3

import hashlib
import base58
import ecdsa
import os
from tqdm import tqdm

def multiply_pq_to_private_key(p, q):
	"""
	Multiply p and q to get private key
	"""
	return (p * q) % (2**256)

def private_key_to_wif(private_key_int, compressed=True):
	"""
	Convert private key integer to Wallet Import Format (WIF)
	"""
	# Add version byte (0x80 for mainnet)
	private_key_bytes = private_key_int.to_bytes(32, byteorder='big')
	versioned_key = b'\x80' + private_key_bytes
	
	if compressed:
		versioned_key += b'\x01'
	
	# Double SHA256 hash
	first_sha = hashlib.sha256(versioned_key).digest()
	second_sha = hashlib.sha256(first_sha).digest()
	
	# Add checksum (first 4 bytes of the hash)
	checksum = second_sha[:4]
	
	# Combine and encode as base58
	wif_key = versioned_key + checksum
	return base58.b58encode(wif_key).decode('ascii')

def private_key_to_public_key(private_key_int, compressed=True):
	"""
	Convert private key to public key using secp256k1
	"""
	# SECP256k1 curve parameters
	sk = ecdsa.SigningKey.from_string(private_key_int.to_bytes(32, byteorder='big'), curve=ecdsa.SECP256k1)
	vk = sk.get_verifying_key()
	
	if compressed:
		# Compressed public key format
		x = vk.pubkey.point.x()
		y = vk.pubkey.point.y()
		if y % 2 == 0:
			public_key = b'\x02' + x.to_bytes(32, byteorder='big')
		else:
			public_key = b'\x03' + x.to_bytes(32, byteorder='big')
	else:
		# Uncompressed public key format
		public_key = b'\x04' + vk.pubkey.point.x().to_bytes(32, byteorder='big') + vk.pubkey.point.y().to_bytes(32, byteorder='big')
	
	return public_key.hex()

def public_key_to_address(public_key_hex, compressed=True):
	"""
	Convert public key to Bitcoin address
	"""
	public_key_bytes = bytes.fromhex(public_key_hex)
	
	# SHA256 hash
	sha256_hash = hashlib.sha256(public_key_bytes).digest()
	
	# RIPEMD160 hash
	ripemd160_hash = hashlib.new('ripemd160')
	ripemd160_hash.update(sha256_hash)
	hash160 = ripemd160_hash.digest()
	
	# Add network byte (0x00 for mainnet)
	versioned_hash = b'\x00' + hash160
	
	# Double SHA256 for checksum
	first_sha = hashlib.sha256(versioned_hash).digest()
	second_sha = hashlib.sha256(first_sha).digest()
	checksum = second_sha[:4]
	
	# Combine and encode as base58
	binary_address = versioned_hash + checksum
	return base58.b58encode(binary_address).decode('ascii')

def main():

	os.system('cls' if os.name == 'nt' else 'clear')

	r=[]
	r.append(0x00000000000000000000003b78ce563f89a0ed9414f5aa28ad0d96d6795f9c63)
	r.append(115792089237316195423570985008687907852837564279074904382605163141518161494337)
	r.append(55066263022277343669578718895168534326250603453777594175500187360389116729240)
	r.append(32670510020758816978083085130507043184471273380659243275938904335757337482424)
	r.append(0x0089848a1c90ee587b1d8b71c9bafccbc072613e41b3fd38cc2b1cf3041e3792bc)
	r.append(0x45305be296870b32cca5dac0f0972cac820090214158652581f406fc70ef30f3)
	r.append(0x3d4a58fa8e5f94e9b8ed1d79a2d584ce45803153b75d43d7bcdbf49171d90992)
	r.append(10142789312725007)
	r.append(8114231289041741)
	r.append(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798)
	r.append(0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)

	size=1048576*10

	n=0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

	o=open('output.txt','w')

	c=0

	a=len(r)*len(r)*len(range(-1024,1025))*len(range(-1024,1025))
	t=tqdm(total=a)

	for i in r:
		for j in r:
			for k in range(-1024,1025):
				for l in range(-1024,1025):
					p=i+k
					q=j+l

					# Multiply p and q to get private key
					private_key_int = multiply_pq_to_private_key(p, q)
					
					o.write(f"pvk hex: {private_key_int:064x}\n")
					
					# Generate WIF private keys
					wif_uncompressed = private_key_to_wif(private_key_int, compressed=False)
					wif_compressed = private_key_to_wif(private_key_int, compressed=True)
					
					o.write(f"WIF Unc: {wif_uncompressed}\n")
					o.write(f"WIF Comp: {wif_compressed}\n")
					
					# Generate public keys
					public_key_uncompressed = private_key_to_public_key(private_key_int, compressed=False)
					public_key_compressed = private_key_to_public_key(private_key_int, compressed=True)
					
					#print(f"Public Key (Uncompressed): {public_key_uncompressed}")
					#print(f"Public Key (Compressed): {public_key_compressed}")
					
					# Generate addresses
					address_uncompressed = public_key_to_address(public_key_uncompressed, compressed=False)
					address_compressed = public_key_to_address(public_key_compressed, compressed=True)
					
					o.write(f"Addr Unc: {address_uncompressed}\n")
					o.write(f"Addr Comp: {address_compressed}\n")
					c+=1
					t.update(1)
					#if c%1000==0:
					#	print(f'\r{c}/{a}',end='')
					#print("#"*132)

if __name__ == "__main__":
	main()
