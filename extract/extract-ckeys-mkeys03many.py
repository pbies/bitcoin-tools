#!/usr/bin/env python3
"""
Enhanced Bitcoin Core Wallet.dat Parser with BDB support
"""

import os
import sys
import json
import argparse
from pathlib import Path

def find_wallet_files(start_path):
	"""Recursively find all wallet.dat files in the given directory"""
	wallet_files = []
	start_path = Path(start_path)
	
	if start_path.is_file() and start_path.name == "wallet.dat":
		return [start_path]
	
	for pattern in ["wallet.dat", "*.dat"]:
		wallet_files.extend(start_path.rglob(pattern))

	return wallet_files

def export_results(results, output_format='json'):
	"""Export results in specified format"""
	if output_format == 'json':
		output_file = 'wallet_keys_export.json'
		with open(output_file, 'w') as f:
			json.dump(results, f, indent=2)
		print(f"\nResults exported to: {output_file}")
	
	elif output_format == 'txt':
		output_file = 'wallet_keys_export.txt'
		with open(output_file, 'w') as f:
			for result in results:
				f.write(f"File: {result['file_path']}\n")
				if 'error' in result:
					f.write(f"Error: {result['error']}\n")
				else:
					f.write(f"Found {len(result['ckeys'])} ckeys\n")
					f.write(f"Found {len(result['mkeys'])} mkeys\n")
					
					for i, ckey in enumerate(result['ckeys']):
						f.write(f"  ckey {i+1}: {ckey['value_hex']}\n")
					
					for i, mkey in enumerate(result['mkeys']):
						f.write(f"  mkey {i+1}: {mkey['value_hex']}\n")
				
				f.write("-" * 50 + "\n")
		print(f"\nResults exported to: {output_file}")

def install_dependencies():
	"""Check and install required dependencies"""
	try:
		import bsddb3
	except ImportError:
		print("Installing required dependencies...")
		os.system("pip install bsddb3")
		try:
			import bsddb3
		except ImportError:
			print("Error: bsddb3 installation failed. Please install manually:")
			print("  On Ubuntu: sudo apt-get install libdb-dev")
			print("  Then: pip install bsddb3")
			return False
	return True

def parse_wallet_bdb(wallet_path):
	"""Parse wallet.dat using Berkeley DB"""
	try:
		import bsddb3
		
		keys_data = {
			'file_path': str(wallet_path),
			'ckeys': [],
			'mkeys': [],
			'keys': [],
			'metadata': {}
		}
		
		db = bsddb3.db.DB()
		db.open(str(wallet_path), 'main', bsddb3.db.DB_UNKNOWN, bsddb3.db.DB_RDONLY)
		
		cursor = db.cursor()
		record = cursor.first()
		
		while record:
			key, value = record
			#print(key)
			# Convert key to string for analysis
			try:
				key_str = key.decode('latin-1')[1:]
			except:
				key_str = str(key[1:])
			#print(key_str)
			# Look for different key types
			if key_str.startswith('ckey'):
				keys_data['ckeys'].append({
					'key': key_str,
					'value_hex': value.hex(),
					'value_length': len(value)
				})
			elif key_str.startswith('mkey'):
				keys_data['mkeys'].append({
					'key': key_str,
					'value_hex': value.hex(),
					'value_length': len(value)
				})
			elif key_str.startswith('key'):
				keys_data['keys'].append({
					'key': key_str,
					'value_hex': value.hex(),
					'value_length': len(value)
				})
			elif key_str in ['version', 'minversion', 'walletversion']:
				try:
					version = int.from_bytes(value, 'little')
					keys_data['metadata'][key_str] = version
				except:
					keys_data['metadata'][key_str] = value.hex()
			elif key_str == 'keypool':
				try:
					keypool_size = int.from_bytes(value, 'little')
					keys_data['metadata']['keypool_size'] = keypool_size
				except:
					pass
			
			record = cursor.next()
		
		cursor.close()
		db.close()
		return keys_data
		
	except Exception as e:
		return {
			'file_path': str(wallet_path),
			'error': str(e),
			'ckeys': [],
			'mkeys': []
		}

def main_enhanced():
	if not install_dependencies():
		sys.exit(1)
	
	parser = argparse.ArgumentParser(description='Enhanced Bitcoin Core wallet.dat parser')
	parser.add_argument('path', help='Path to search for wallet.dat files')
	parser.add_argument('--output', '-o', choices=['json', 'txt'], default='json')
	parser.add_argument('--verbose', '-v', action='store_true')
	
	args = parser.parse_args()
	
	wallet_files = find_wallet_files(args.path)
	
	if not wallet_files:
		print("No wallet.dat files found")
		return
	
	print(f"Found {len(wallet_files)} wallet.dat files")
	
	results = []
	for wallet_file in wallet_files:

		if args.verbose:
			print(f"Processing: {wallet_file}")
		
		result = parse_wallet_bdb(wallet_file)
		results.append(result)
		
		if args.verbose:
			if 'error' in result:
				print(f"  Error: {result['error']}")
			else:
				print(f"  Found {len(result['ckeys'])} ckeys, {len(result['mkeys'])} mkeys, {len(result['keys'])} keys")
	
	# Export results
	export_results(results, args.output)

if __name__ == "__main__":
	# Use enhanced version if BDB is available
	if install_dependencies():
		main_enhanced()
	else:
		print("Falling back to basic parser...")
		main()
