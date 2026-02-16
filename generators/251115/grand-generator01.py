#!/usr/bin/env python3

import hashlib
import base58
import ecdsa

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
	print("Bitcoin Key Generator from p and q")
	print("=" * 40)
	
	try:
		# Get p and q from user
		p = int(input("Enter value for p: "))
		q = int(input("Enter value for q: "))
		
		# Multiply p and q to get private key
		private_key_int = multiply_pq_to_private_key(p, q)
		
		print(f"\nGenerated Private Key (integer): {private_key_int}")
		print(f"Generated Private Key (hex): {private_key_int:064x}")
		
		# Generate WIF private keys
		wif_uncompressed = private_key_to_wif(private_key_int, compressed=False)
		wif_compressed = private_key_to_wif(private_key_int, compressed=True)
		
		print(f"\nWIF Private Key (Uncompressed): {wif_uncompressed}")
		print(f"WIF Private Key (Compressed): {wif_compressed}")
		
		# Generate public keys
		public_key_uncompressed = private_key_to_public_key(private_key_int, compressed=False)
		public_key_compressed = private_key_to_public_key(private_key_int, compressed=True)
		
		print(f"\nPublic Key (Uncompressed): {public_key_uncompressed}")
		print(f"Public Key (Compressed): {public_key_compressed}")
		
		# Generate addresses
		address_uncompressed = public_key_to_address(public_key_uncompressed, compressed=False)
		address_compressed = public_key_to_address(public_key_compressed, compressed=True)
		
		print(f"\nBitcoin Address (Uncompressed): {address_uncompressed}")
		print(f"Bitcoin Address (Compressed): {address_compressed}")
		
		print(f"\nSummary:")
		print(f"Private Key: {private_key_int:064x}")
		print(f"WIF Compressed: {wif_compressed}")
		print(f"Address Compressed: {address_compressed}")
		
	except ValueError:
		print("Error: Please enter valid integers for p and q")
	except Exception as e:
		print(f"Error: {e}")

if __name__ == "__main__":
	main()
