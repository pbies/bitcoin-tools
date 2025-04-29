#!/usr/bin/env python3

import itertools
import base58
import hashlib
import ecdsa
from concurrent.futures import ThreadPoolExecutor

# Converts WIF to raw private key
def wif_to_private_key(wif):
	decoded = base58.b58decode_check(wif)
	return decoded[1:] # Remove 0x80 prefix

# Converts raw private key to Bitcoin address
def private_key_to_address(private_key_bytes):
	sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
	vk = sk.get_verifying_key()
	pub_key = b'\x04' + vk.to_string()

	sha256_1 = hashlib.sha256(pub_key).digest()
	ripemd160 = hashlib.new('ripemd160')
	ripemd160.update(sha256_1)
	hashed_pubkey = ripemd160.digest()

	mainnet_pubkey = b'\x00' + hashed_pubkey
	checksum = hashlib.sha256(hashlib.sha256(mainnet_pubkey).digest()).digest()[:4]
	binary_address = mainnet_pubkey + checksum
	address = base58.b58encode(binary_address)
	return address.decode()

# Worker function: tries a guess
def try_guess(guess_tuple, wif_partial, target_address):
	guess_str = ''.join(guess_tuple)
	try_wif = wif_partial.replace('?' * len(guess_tuple), guess_str)
	try:
		private_key_bytes = wif_to_private_key(try_wif)
		derived_address = private_key_to_address(private_key_bytes)
		if derived_address == target_address:
			print(f"\nSUCCESS! Full WIF: {try_wif}")
			return try_wif
	except Exception:
		return None
	return None

def bruteforce_multithreaded(wif_partial, missing_count, target_address, max_workers=8):
	charset = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

	# Prepare all combinations
	combinations = itertools.product(charset, repeat=missing_count)

	with ThreadPoolExecutor(max_workers=max_workers) as executor:
		futures = []
		for guess_tuple in combinations:
			futures.append(executor.submit(try_guess, guess_tuple, wif_partial, target_address))

			for future in futures:
				result = future.result()
				if result:
					print(f"\nFound matching WIF: {result}")
					return result

			print("No match found.")
			return None

def main():
	# Example: partial WIF with two missing characters
	partial_wif = '5Kb8kLf9zgWQnogidDA76MzPL6TsZZY36hWvm??' # Two '?' missing
	missing_chars = partial_wif.count('?')

	# Target Bitcoin address
	target_address = '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'

	bruteforce_multithreaded(partial_wif, missing_chars, target_address, max_workers=16)

if __name__ == "__main__":
	main()
