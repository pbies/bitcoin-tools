#!/usr/bin/env python3

import base58
import hashlib
import binascii
import os

def private_key_to_wif(private_key_hex, compressed=True, testnet=False):
	"""
	Convert a private key (hex) to WIF format
	
	Args:
		private_key_hex: Private key in hexadecimal format (64 chars)
		compressed: Whether to use compressed public key format
		testnet: Whether to use testnet prefix
	
	Returns:
		WIF string
	"""
	# Validate private key length
	if len(private_key_hex) != 64:
		raise ValueError("Private key must be 64 hex characters (32 bytes)")
	
	# Add prefix
	# Mainnet: 0x80, Testnet: 0xEF
	prefix = b'\xef' if testnet else b'\x80'
	
	# Convert hex to bytes
	private_key_bytes = binascii.unhexlify(private_key_hex)
	
	# Add compression flag if using compressed format
	if compressed:
		payload = prefix + private_key_bytes + b'\x01'
	else:
		payload = prefix + private_key_bytes
	
	# Calculate checksum (first 4 bytes of double SHA256)
	checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
	
	# Combine payload and checksum
	wif_bytes = payload + checksum
	
	# Encode in Base58
	wif = base58.b58encode(wif_bytes)
	
	return wif.decode('utf-8')

def wif_to_private_key(wif_string):
	"""
	Convert a WIF string to private key (hex)
	
	Args:
		wif_string: WIF string
	
	Returns:
		tuple: (private_key_hex, compressed, testnet)
	"""
	# Decode Base58
	wif_bytes = base58.b58decode(wif_string)
	
	# Validate length
	if len(wif_bytes) not in [37, 38]:  # Uncompressed: 37 bytes, Compressed: 38 bytes
		raise ValueError("Invalid WIF length")
	
	# Extract components
	version_byte = wif_bytes[0]
	testnet = version_byte == 0xef
	
	# Check version byte
	if version_byte not in [0x80, 0xef]:
		raise ValueError(f"Invalid version byte: {hex(version_byte)}")
	
	# Check if compressed (ends with 0x01 before checksum)
	compressed = len(wif_bytes) == 38 and wif_bytes[-5] == 0x01
	
	# Extract private key
	if compressed:
		private_key_bytes = wif_bytes[1:-5]
	else:
		private_key_bytes = wif_bytes[1:-4]
	
	# Verify checksum
	payload = wif_bytes[:-4]
	checksum = wif_bytes[-4:]
	calculated_checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
	
	if checksum != calculated_checksum:
		raise ValueError("Invalid WIF checksum")
	
	# Convert to hex
	private_key_hex = binascii.hexlify(private_key_bytes).decode('utf-8')
	
	return private_key_hex, compressed, testnet

def generate_private_key():
	"""
	Generate a random private key
	
	Returns:
		Private key in hex format
	"""
	# Generate 32 random bytes
	private_key = os.urandom(32)
	
	# Convert to hex and ensure it's valid (within SECP256k1 range)
	private_key_hex = binascii.hexlify(private_key).decode('utf-8')
	
	# Check if key is in valid range (1 to n-1 where n is curve order)
	# For simplicity, we'll just ensure it's not all zeros
	if private_key_hex == '0' * 64:
		return generate_private_key()  # Try again if all zeros
	
	return private_key_hex

def validate_wif(wif_string):
	"""
	Validate a WIF string
	
	Args:
		wif_string: WIF string to validate
	
	Returns:
		bool: True if valid
	"""
	try:
		wif_to_private_key(wif_string)
		return True
	except:
		return False

# Example usage and test functions
def main():
	print("=" * 60)
	print("Bitcoin WIF Converter")
	print("=" * 60)
	
	# Example 1: Generate and convert a private key
	print("\n1. Generating a random private key and converting to WIFs:")
	
	private_key = generate_private_key()
	print(f"Private Key (hex): {private_key}")
	
	# Convert to different WIF formats
	wif_compressed = private_key_to_wif(private_key, compressed=True, testnet=False)
	wif_uncompressed = private_key_to_wif(private_key, compressed=False, testnet=False)
	wif_testnet_compressed = private_key_to_wif(private_key, compressed=True, testnet=True)
	
	print(f"WIF Compressed (Mainnet): {wif_compressed}")
	print(f"WIF Uncompressed (Mainnet): {wif_uncompressed}")
	print(f"WIF Compressed (Testnet): {wif_testnet_compressed}")
	
	# Example 2: Convert WIF back to private key
	print("\n2. Converting WIFs back to private keys:")
	
	test_wifs = [wif_compressed, wif_uncompressed, wif_testnet_compressed]
	
	for wif in test_wifs:
		try:
			priv_key, compressed, testnet = wif_to_private_key(wif)
			print(f"\nWIF: {wif}")
			print(f"  Private Key: {priv_key}")
			print(f"  Compressed: {compressed}")
			print(f"  Testnet: {testnet}")
			print(f"  Valid: {validate_wif(wif)}")
		except Exception as e:
			print(f"\nError processing {wif}: {e}")
	
	# Example 3: Test with known WIFs
	print("\n3. Testing with known Bitcoin WIFs:")
	
	known_wifs = [
		# From Bitcoin documentation
		("5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ", False, False),
		("KwdMAjGmerYanjeui5SHS7JkmpZvVipYvB2LJGU1ZxJwYvP98617", True, False),
		("cTAKELgriHH5VcP6fGg9QZgq7Hd6L8cBgsJRJNt2L5kF5aMJmQet", True, True),  # Testnet
	]
	
	for wif, expected_compressed, expected_testnet in known_wifs:
		try:
			priv_key, compressed, testnet = wif_to_private_key(wif)
			print(f"\nWIF: {wif}")
			print(f"  Private Key: {priv_key}")
			print(f"  Compressed: {compressed} (expected: {expected_compressed})")
			print(f"  Testnet: {testnet} (expected: {expected_testnet})")
			print(f"  Valid: {validate_wif(wif)}")
			
			# Convert back to WIF to verify
			regenerated_wif = private_key_to_wif(
				priv_key, 
				compressed=compressed, 
				testnet=testnet
			)
			print(f"  Regenerated WIF matches: {regenerated_wif == wif}")
			
		except Exception as e:
			print(f"\nError processing known WIF {wif}: {e}")
	
	# Interactive mode
	print("\n4. Interactive conversion:")
	print("   Enter 'q' to quit")
	
	while True:
		print("\n" + "-" * 40)
		choice = input("Choose direction:\n1. Private Key -> WIF\n2. WIF -> Private Key\n> ")
		
		if choice.lower() == 'q':
			break
		
		if choice == '1':
			priv_key = input("Enter private key (hex, 64 chars): ").strip()
			if len(priv_key) != 64:
				print("Error: Private key must be 64 hex characters")
				continue
			
			compressed = input("Compressed? (y/n): ").strip().lower() == 'y'
			testnet = input("Testnet? (y/n): ").strip().lower() == 'y'
			
			try:
				wif = private_key_to_wif(priv_key, compressed=compressed, testnet=testnet)
				print(f"\nResult: {wif}")
			except Exception as e:
				print(f"Error: {e}")
		
		elif choice == '2':
			wif = input("Enter WIF: ").strip()
			
			try:
				priv_key, compressed, testnet = wif_to_private_key(wif)
				print(f"\nPrivate Key (hex): {priv_key}")
				print(f"Compressed: {compressed}")
				print(f"Testnet: {testnet}")
			except Exception as e:
				print(f"Error: {e}")
		
		else:
			print("Invalid choice. Enter 1, 2, or 'q' to quit.")

if __name__ == "__main__":
	# Install required package if not already installed
	try:
		import base58
	except ImportError:
		print("Installing base58 package...")
		import subprocess
		import sys
		subprocess.check_call([sys.executable, "-m", "pip", "install", "base58"])
		import base58
	
	main()
