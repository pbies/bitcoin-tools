#!/usr/bin/env python3

import base58
import hashlib
import binascii
import sys

def wif_to_private_key(wif):
	"""
	Convert WIF to private key (hex) and extract format info
	
	Args:
		wif: Wallet Import Format string
	
	Returns:
		tuple: (private_key_hex, compressed, testnet)
	"""
	try:
		# Decode Base58
		wif_bytes = base58.b58decode(wif)
		
		# Validate length
		if len(wif_bytes) not in [37, 38]:
			raise ValueError("Invalid WIF length")
		
		# Extract version byte
		version_byte = wif_bytes[0]
		
		# Determine network
		# Mainnet: 0x80, Testnet: 0xEF
		testnet = version_byte == 0xef
		if version_byte not in [0x80, 0xef]:
			raise ValueError(f"Invalid version byte: {hex(version_byte)}")
		
		# Check if compressed (ends with 0x01 before checksum)
		compressed = len(wif_bytes) == 38 and wif_bytes[-5] == 0x01
		
		# Extract private key bytes
		if compressed:
			private_key_bytes = wif_bytes[1:-5]  # Skip version byte and 0x01 compression flag
		else:
			private_key_bytes = wif_bytes[1:-4]  # Skip version byte
		
		# Verify checksum
		payload = wif_bytes[:-4]
		checksum = wif_bytes[-4:]
		calculated_checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
		
		if checksum != calculated_checksum:
			raise ValueError("Invalid WIF checksum")
		
		# Convert to hex
		private_key_hex = binascii.hexlify(private_key_bytes).decode('utf-8')
		
		return private_key_hex, compressed, testnet
	
	except Exception as e:
		raise ValueError(f"Invalid WIF format: {e}")

def private_key_to_wif(private_key_hex, compressed=True, testnet=False):
	"""
	Convert private key (hex) to WIF format
	
	Args:
		private_key_hex: Private key in hexadecimal (64 chars)
		compressed: Whether to create compressed WIF
		testnet: Whether to create testnet WIF
	
	Returns:
		WIF string
	"""
	# Validate private key
	if len(private_key_hex) != 64:
		raise ValueError("Private key must be 64 hex characters (32 bytes)")
	
	# Convert hex to bytes
	try:
		private_key_bytes = binascii.unhexlify(private_key_hex)
	except:
		raise ValueError("Invalid hex string")
	
	# Set version byte
	# Mainnet: 0x80, Testnet: 0xEF
	version_byte = b'\xef' if testnet else b'\x80'
	
	# Create payload
	if compressed:
		payload = version_byte + private_key_bytes + b'\x01'
	else:
		payload = version_byte + private_key_bytes
	
	# Calculate checksum
	checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
	
	# Combine and encode
	wif_bytes = payload + checksum
	wif = base58.b58encode(wif_bytes).decode('utf-8')
	
	return wif

def convert_wif_compression(wif, to_compressed=True):
	"""
	Convert WIF between compressed and uncompressed formats
	
	Args:
		wif: Input WIF string
		to_compressed: True to convert to compressed, False for uncompressed
	
	Returns:
		Converted WIF string
	"""
	# Decode WIF to get private key and current format
	private_key_hex, current_compressed, testnet = wif_to_private_key(wif)
	
	# If already in desired format, return original
	if current_compressed == to_compressed:
		return wif
	
	# Convert to desired format
	new_wif = private_key_to_wif(private_key_hex, compressed=to_compressed, testnet=testnet)
	
	return new_wif

def detect_wif_format(wif):
	"""
	Detect and return information about WIF format
	
	Args:
		wif: WIF string
	
	Returns:
		dict with format information
	"""
	try:
		private_key_hex, compressed, testnet = wif_to_private_key(wif)
		
		# Determine format string
		if testnet:
			network = "Testnet"
			if compressed:
				expected_prefix = "c"  # Testnet compressed WIFs start with 'c'
			else:
				expected_prefix = "9"  # Testnet uncompressed WIFs start with '9'
		else:
			network = "Mainnet"
			if compressed:
				expected_prefix = "K or L"  # Mainnet compressed WIFs start with K or L
			else:
				expected_prefix = "5"  # Mainnet uncompressed WIFs start with 5
		
		return {
			"valid": True,
			"private_key": private_key_hex,
			"compressed": compressed,
			"testnet": testnet,
			"network": network,
			"expected_prefix": expected_prefix,
			"actual_prefix": wif[0],
			"length": len(wif)
		}
	except Exception as e:
		return {
			"valid": False,
			"error": str(e)
		}

def batch_convert_wifs(wif_list, to_compressed=True):
	"""
	Convert multiple WIFs between formats
	
	Args:
		wif_list: List of WIF strings
		to_compressed: Target format (True for compressed, False for uncompressed)
	
	Returns:
		List of converted WIFs
	"""
	results = []
	for wif in wif_list:
		try:
			converted = convert_wif_compression(wif, to_compressed)
			results.append({
				"original": wif,
				"converted": converted,
				"success": True
			})
		except Exception as e:
			results.append({
				"original": wif,
				"error": str(e),
				"success": False
			})
	return results

def main():
	print("=" * 70)
	print("BITCOIN WIF COMPRESSION CONVERTER")
	print("=" * 70)
	print("\nThis tool converts between compressed and uncompressed WIF formats.")
	print("Compressed WIFs are shorter and produce compressed public keys.")
	print("Uncompressed WIFs are legacy format.")
	print("-" * 70)
	
	# Example WIFs for demonstration
	example_wifs = {
		"uncompressed_mainnet": "5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ",
		"compressed_mainnet": "KwdMAjGmerYanjeui5SHS7JkmpZvVipYvB2LJGU1ZxJwYvP98617",
		"uncompressed_testnet": "91gGn1HgC8Y3q1F7qA4p6QZ7p7XQtJqZBwQqUQqoZJ5qYtqKZvF",
		"compressed_testnet": "cTAKELgriHH5VcP6fGg9QZgq7Hd6L8cBgsJRJNt2L5kF5aMJmQet"
	}
	
	while True:
		print("\n" + "=" * 70)
		print("MENU:")
		print("1. Convert WIF to different compression format")
		print("2. Detect WIF format information")
		print("3. Batch convert multiple WIFs")
		print("4. Show examples")
		print("5. Exit")
		print("-" * 70)
		
		choice = input("\nEnter your choice (1-5): ").strip()
		
		if choice == "1":
			print("\n--- SINGLE WIF CONVERSION ---")
			wif = input("Enter WIF: ").strip()
			
			# Detect current format
			format_info = detect_wif_format(wif)
			if not format_info["valid"]:
				print(f"❌ Invalid WIF: {format_info['error']}")
				continue
			
			print(f"\nCurrent format:")
			print(f"  Network: {format_info['network']}")
			print(f"  Compression: {'Compressed' if format_info['compressed'] else 'Uncompressed'}")
			print(f"  Private key: {format_info['private_key']}")
			
			# Ask for target format
			target_format = input(f"\nConvert to {'uncompressed' if format_info['compressed'] else 'compressed'}? (y/n): ").strip().lower()
			
			if target_format == 'y':
				to_compressed = not format_info['compressed']
				try:
					converted_wif = convert_wif_compression(wif, to_compressed)
					print(f"\n✅ Conversion successful!")
					print(f"Original WIF:   {wif}")
					print(f"Converted WIF:  {converted_wif}")
					print(f"New format:	 {'Compressed' if to_compressed else 'Uncompressed'} {format_info['network']}")
				except Exception as e:
					print(f"❌ Conversion failed: {e}")
			else:
				print("Conversion cancelled.")
		
		elif choice == "2":
			print("\n--- WIF FORMAT DETECTION ---")
			wif = input("Enter WIF: ").strip()
			
			format_info = detect_wif_format(wif)
			
			if format_info["valid"]:
				print(f"\n✅ Valid WIF detected:")
				print(f"  Network:		 {format_info['network']}")
				print(f"  Compression:	 {'Compressed' if format_info['compressed'] else 'Uncompressed'}")
				print(f"  Private Key:	 {format_info['private_key']}")
				print(f"  Expected Prefix: {format_info['expected_prefix']}")
				print(f"  Actual Prefix:   {format_info['actual_prefix']}")
				print(f"  Length:		  {format_info['length']} characters")
				
				# Check if prefix matches expected
				actual = format_info['actual_prefix']
				expected = format_info['expected_prefix']
				if ' or ' in expected:
					expected_list = expected.split(' or ')
					if actual not in expected_list:
						print(f"  ⚠️  Prefix warning: Got '{actual}', expected {expected}")
				elif actual != expected:
					print(f"  ⚠️  Prefix warning: Got '{actual}', expected '{expected}'")
			else:
				print(f"\n❌ Invalid WIF: {format_info['error']}")
		
		elif choice == "3":
			print("\n--- BATCH CONVERSION ---")
			print("Enter WIFs (one per line). Enter 'done' when finished:")
			
			wif_list = []
			while True:
				wif = input().strip()
				if wif.lower() == 'done':
					break
				if wif:
					wif_list.append(wif)
			
			if not wif_list:
				print("No WIFs entered.")
				continue
			
			target = input("\nConvert to (c)ompressed or (u)ncompressed? (c/u): ").strip().lower()
			to_compressed = target == 'c'
			
			print(f"\nConverting {len(wif_list)} WIFs to {'compressed' if to_compressed else 'uncompressed'}...")
			results = batch_convert_wifs(wif_list, to_compressed)
			
			print("\nResults:")
			print("-" * 70)
			for result in results:
				if result["success"]:
					print(f"✅ {result['original'][:20]}... -> {result['converted'][:20]}...")
				else:
					print(f"❌ {result['original'][:20]}... -> ERROR: {result['error']}")
		
		elif choice == "4":
			print("\n--- EXAMPLE WIFs ---")
			print("These are example WIFs (not real funds):")
			print("\nMainnet:")
			print(f"  Uncompressed: {example_wifs['uncompressed_mainnet']}")
			print(f"  Compressed:   {example_wifs['compressed_mainnet']}")
			print("\nTestnet:")
			print(f"  Uncompressed: {example_wifs['uncompressed_testnet']}")
			print(f"  Compressed:   {example_wifs['compressed_testnet']}")
			
			print("\nTry converting between formats:")
			test_wif = input("\nEnter an example WIF to test (or press Enter to skip): ").strip()
			if test_wif:
				format_info = detect_wif_format(test_wif)
				if format_info["valid"]:
					to_compressed = not format_info['compressed']
					converted = convert_wif_compression(test_wif, to_compressed)
					print(f"\nOriginal:  {test_wif}")
					print(f"Converted: {converted}")
					print(f"Format: {'Compressed' if to_compressed else 'Uncompressed'} -> {'Uncompressed' if to_compressed else 'Compressed'}")
				else:
					print(f"Invalid WIF: {format_info['error']}")
		
		elif choice == "5":
			print("\nExiting. Goodbye!")
			break
		
		else:
			print("Invalid choice. Please enter 1-5.")
		
		input("\nPress Enter to continue...")

if __name__ == "__main__":
	# Check if base58 is installed
	try:
		import base58
	except ImportError:
		print("Installing required package: base58")
		import subprocess
		import sys
		subprocess.check_call([sys.executable, "-m", "pip", "install", "base58"])
		import base58
	
	# ASCII Art
	bitcoin_art = """
	╔════════════════════════════════════════════════════════╗
	║   ██████╗ ██╗████████╗ ██████╗ ██████╗ ██╗███╗   ██╗   ║
	║   ██╔══██╗██║╚══██╔══╝██╔════╝██╔═══██╗██║████╗  ██║   ║
	║   ██████╔╝██║   ██║   ██║     ██║   ██║██║██╔██╗ ██║   ║
	║   ██╔══██╗██║   ██║   ██║     ██║   ██║██║██║╚██╗██║   ║
	║   ██████╔╝██║   ██║   ╚██████╗╚██████╔╝██║██║ ╚████║   ║
	║   ╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝   ║
	║                                                        ║
	║         WIF Compression Format Converter v1.0          ║
	╚════════════════════════════════════════════════════════╝
	"""
	
	print(bitcoin_art)
	main()
