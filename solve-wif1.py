#!/usr/bin/env python3

import itertools
import base58
import hashlib
import ecdsa

def wif_to_private_key(wif):
	# Decode WIF to get the raw private key
	decoded = base58.b58decode_check(wif)
	return decoded[1:] # Remove 0x80 prefix

def private_key_to_address(private_key_bytes):
	# Get the public key
	sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
	vk = sk.get_verifying_key()
	pub_key = b'\x04' + vk.to_string()

	# SHA256
	sha256_1 = hashlib.sha256(pub_key).digest()
	# RIPEMD-160
	ripemd160 = hashlib.new('ripemd160')
	ripemd160.update(sha256_1)
	hashed_pubkey = ripemd160.digest()

	# Mainnet address
	mainnet_pubkey = b'\x00' + hashed_pubkey
	checksum = hashlib.sha256(hashlib.sha256(mainnet_pubkey).digest()).digest()[:4]
	binary_address = mainnet_pubkey + checksum
	address = base58.b58encode(binary_address)
	return address.decode()

def bruteforce_missing(wif_partial, missing_count, target_address):
	charset = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz' # Base58 chars
	for guess in itertools.product(charset, repeat=missing_count):
		guess_str = ''.join(guess)
		try_wif = wif_partial.replace('?', guess_str)
		try:
			private_key_bytes = wif_to_private_key(try_wif)
			derived_address = private_key_to_address(private_key_bytes)
			if derived_address == target_address:
				print(f"SUCCESS! Full WIF: {try_wif}")
				return try_wif
		except Exception:
			continue
			print("No match found.")
			return None

def main():
	# Example (you have partial WIF, with '?' placeholders for missing parts)
	partial_wif = '5Kb8kLf9zgWQnogidDA76MzPL6TsZZY36hWvmM?G' # '?' = missing 1 char
	missing_chars = partial_wif.count('?')

	# Target Bitcoin address (from the puzzle)
	target_address = '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'

	bruteforce_missing(partial_wif, missing_chars, target_address)

if __name__ == "__main__":
	main()
