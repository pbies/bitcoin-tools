#!/usr/bin/env python3
# enhanced_crypto.py (additional cryptographic functions)
import hashlib
import ecdsa
import base58

def private_key_to_hash160(private_key_int):
	"""Convert private key integer to hash160 (proper implementation)"""
	# Convert to bytes (32 bytes, big-endian)
	priv_key_bytes = private_key_int.to_bytes(32, 'big')
	
	# Get public key using secp256k1
	sk = ecdsa.SigningKey.from_string(priv_key_bytes, curve=ecdsa.SECP256k1)
	vk = sk.verifying_key
	public_key_bytes = b'\x04' + vk.to_string()  # Uncompressed public key
	
	# SHA256
	sha256_hash = hashlib.sha256(public_key_bytes).digest()
	
	# RIPEMD-160
	ripemd160 = hashlib.new('ripemd160')
	ripemd160.update(sha256_hash)
	hash160 = ripemd160.digest()
	
	return hash160

def hash160_to_address(hash160_bytes):
	"""Convert hash160 to Bitcoin address"""
	# Add version byte (0x00 for mainnet)
	versioned_payload = b'\x00' + hash160_bytes
	
	# Double SHA256 for checksum
	checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
	
	# Base58 encode
	return base58.b58encode(versioned_payload + checksum).decode('utf-8')
