#!/usr/bin/env python3

import hashlib
import base58

def hex_to_wif(private_key_hex, compressed=True, testnet=False):
	"""
	Convert a private key from hex to WIF format
	
	Args:
		private_key_hex (str): Private key in hexadecimal format
		compressed (bool): Whether to use compressed public key format
		testnet (bool): Whether to use testnet prefix
	
	Returns:
		str: WIF formatted private key
	"""
	
	# Validate hex input
	if not all(c in '0123456789abcdefABCDEF' for c in private_key_hex):
		raise ValueError("Invalid hexadecimal string")
	
	# Remove any spaces and convert to lowercase
	private_key_hex = private_key_hex.strip().lower()
	
	# Check if hex has 0x prefix and remove it
	if private_key_hex.startswith('0x'):
		private_key_hex = private_key_hex[2:]
	
	# Ensure the private key is 64 characters (32 bytes)
	if len(private_key_hex) != 64:
		raise ValueError("Private key must be 64 hexadecimal characters (32 bytes)")
	
	# Convert hex to bytes
	try:
		private_key_bytes = bytes.fromhex(private_key_hex)
	except ValueError as e:
		raise ValueError(f"Invalid hex string: {e}")
	
	# Step 1: Add version byte prefix
	# Mainnet: 0x80, Testnet: 0xEF
	version_byte = b'\xef' if testnet else b'\x80'
	extended_key = version_byte + private_key_bytes
	
	# Step 2: Add compression byte if requested
	if compressed:
		extended_key += b'\x01'
	
	# Step 3: Double SHA256 hash
	first_sha = hashlib.sha256(extended_key).digest()
	second_sha = hashlib.sha256(first_sha).digest()
	
	# Step 4: Take first 4 bytes as checksum
	checksum = second_sha[:4]
	
	# Step 5: Append checksum to extended key
	final_bytes = extended_key + checksum
	
	# Step 6: Encode in Base58
	wif = base58encode(final_bytes)
	
	return wif

def base58encode(data):
	"""
	Base58 encoding implementation
	"""
	# Base58 alphabet (excluding 0, O, I, l to avoid confusion)
	alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
	
	# Convert bytes to integer
	n = int.from_bytes(data, 'big')
	
	# Encode in base58
	encoded = ''
	while n > 0:
		n, remainder = divmod(n, 58)
		encoded = alphabet[remainder] + encoded
	
	# Add leading '1's for each leading zero byte
	leading_zeros = 0
	for byte in data:
		if byte == 0:
			leading_zeros += 1
		else:
			break
	
	return '1' * leading_zeros + encoded

def validate_private_key_range(private_key_hex):
	"""
	Validate that the private key is within the valid range for secp256k1
	"""
	private_key_int = int(private_key_hex, 16)
	max_key = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
	
	if private_key_int == 0:
		raise ValueError("Private key cannot be zero")
	if private_key_int >= max_key:
		raise ValueError("Private key is too large (must be less than secp256k1 curve order)")
	
	return True

# Example usage and test cases
if __name__ == "__main__":
	# Test cases with known values
	test_cases = [
		# (hex_private_key, compressed, testnet, expected_wif)
		(
			"0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D",
			False,
			False,
			"5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ"
		),
		(
			"1E99423A4ED27608A15A2616A2B0E9E52CED330AC530EDCC32C8FFC6A526AEDD",
			True,
			False,
			"KxFC1jmwwCoACiCAWZ3eXa96mBM6tb3TYzGmf6YwgdGWZgawvrtJ"
		)
	]
	
	print("Private Key Hex to WIF Converter")
	print("=" * 40)
	
	# Run test cases
	for i, (hex_key, compressed, testnet, expected) in enumerate(test_cases, 1):
		try:
			wif = hex_to_wif(hex_key, compressed, testnet)
			status = "✓" if wif == expected else "✗"
			print(f"Test {i}: {status}")
			print(f"  Input:	{hex_key}")
			print(f"  Compressed: {compressed}, Testnet: {testnet}")
			print(f"  Expected: {expected}")
			print(f"  Got:	  {wif}")
			print()
		except Exception as e:
			print(f"Test {i} failed: {e}")
			print()
	
	# Interactive mode
	print("\nInteractive Mode:")
	print("Enter a private key in hex format (or 'quit' to exit):")
	
	while True:
		try:
			user_input = input("\nPrivate Key (hex): ").strip()
			
			if user_input.lower() in ['quit', 'exit', 'q']:
				break
			
			if not user_input:
				continue
			
			# Ask for compression
			comp_input = input("Compressed? (y/n, default=y): ").strip().lower()
			compressed = comp_input != 'n'
			
			# Ask for testnet
			test_input = input("Testnet? (y/n, default=n): ").strip().lower()
			testnet = test_input == 'y'
			
			# Validate private key range
			validate_private_key_range(user_input)
			
			# Convert to WIF
			wif_result = hex_to_wif(user_input, compressed, testnet)
			
			print(f"\nResult:")
			print(f"  Private Key (hex): {user_input}")
			print(f"  WIF Format: {wif_result}")
			print(f"  Compression: {'Yes' if compressed else 'No'}")
			print(f"  Network: {'Testnet' if testnet else 'Mainnet'}")
			
		except ValueError as e:
			print(f"Error: {e}")
		except KeyboardInterrupt:
			print("\nExiting...")
			break
		except Exception as e:
			print(f"Unexpected error: {e}")

# Basic usage
hex_key = "1E99423A4ED27608A15A2616A2B0E9E52CED330AC530EDCC32C8FFC6A526AEDD"
wif = hex_to_wif(hex_key, compressed=True, testnet=False)
print(wif)  # KxFC1jmwwCoACiCAWZ3eXa96mBM6tb3TYzGmf6YwgdGWZgawvrtJ
