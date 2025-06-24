#!/usr/bin/env python3

# need to fix

import os
import shutil
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

def get_wallet_balance(rpc_connection, wallet_name):
	"""Get the balance of a wallet in BTC"""
	try:
		# Load the wallet if not already loaded
		if wallet_name not in rpc_connection.listwallets():
			rpc_connection.loadwallet(wallet_name)
		
		# Get the balance
		balance = rpc_connection.getbalance()
		return balance
	except JSONRPCException as e:
		print(f"Error getting balance for {wallet_name}: {e}")
		return None

def rename_wallet_with_balance(rpc_connection, wallet_path, new_directory=None):
	"""Rename wallet.dat file to include balance in the filename"""
	try:
		wallet_dir, wallet_file = os.path.split(wallet_path)
		wallet_name = os.path.splitext(wallet_file)[0]
		os.makedirs(wallet_dir+'/'+wallet_file[:-4])
		
		# Get balance
		balance = get_wallet_balance(rpc_connection, wallet_name)
		if balance is None:
			return False
		
		# Create new filename
		balance_btc = round(balance, 8)
		new_filename = f"{wallet_name} - {balance_btc:.8f} BTC.dat"
		
		# Determine output directory
		output_dir = new_directory if new_directory else wallet_dir
		
		# Create new path
		new_path = os.path.join(output_dir, new_filename)
		
		# Copy the wallet file (safer than moving)
		#shutil.copy2(wallet_path, new_path)
		print(f"Renamed: {wallet_path} -> {new_path}")
		return True
	except Exception as e:
		print(f"Error processing {wallet_path}: {e}")
		return False

def main():
	# Bitcoin Core RPC configuration
	rpc_user = "userek"
	rpc_password = "haselko"
	rpc_host = "127.0.0.1"
	rpc_port = "8332"
	
	# Directory containing wallet.dat files
	wallet_dir = "/mnt/d/Bitcoin/wallets"
	#wallet_dir = os.path.expanduser(wallet_dir)
	
	# Optional: Directory to save renamed wallets (None = same directory)
	output_dir = None  # or set to a different path
	
	# Connect to Bitcoin Core
	rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_host}:{rpc_port}/")
	
	# Process all wallet.dat files in the directory
	for wallet_name in os.listdir(wallet_dir):
		if wallet_name[-4:]!='.dat':
			continue
		wallet_path = os.path.join(wallet_dir, wallet_name)
		if os.path.exists(wallet_path):
			rename_wallet_with_balance(rpc_connection, wallet_path, output_dir)
	
	print("Processing complete.")

if __name__ == "__main__":
	main()
