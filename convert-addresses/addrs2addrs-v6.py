#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from concurrent.futures import ProcessPoolExecutor
import base58
import hashlib
import sys

# Function Definitions
def shahex(x):
	"""Compute the SHA-256 hash of a given input."""
	return hashlib.sha256(x.encode()).hexdigest()

def pvk_to_wif2(key_hex):
	"""Convert a hexadecimal private key to Wallet Import Format (WIF)."""
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex))

def go(k):
	"""Generate wallet information and write to the shared output file."""
	l = shahex(k)  # Compute SHA-256 hash of input key
	hdwallet = HDWallet(symbol=BTC)  # Initialize HDWallet for BTC
	hdwallet.from_private_key(private_key=l)

	# Collect all wallet information
	results = [
		pvk_to_wif2(l).decode(),
		hdwallet.wif(),
		hdwallet.p2pkh_address(),
		hdwallet.p2sh_address(),
		hdwallet.p2wpkh_address(),
		hdwallet.p2wpkh_in_p2sh_address(),
		hdwallet.p2wsh_address(),
		hdwallet.p2wsh_in_p2sh_address()
	]

	# Return the results as a formatted string
	return "\n".join(results) + "\n\n"

# Optimized script entry point
def main():
	print("Reading input...", flush=True)

	# Reading input file using a generator to save memory
	with open(sys.argv[1], 'r') as infile:
		lines = (line.strip() for line in infile)

		print("Writing output...", flush=True)

		# Using ProcessPoolExecutor for better control and optimization
		with open(sys.argv[1]+'.out', 'w') as outfile:
			with ProcessPoolExecutor(max_workers=24) as executor:
				for result in executor.map(go, lines, chunksize=10000):
					outfile.write(result)

	print("\a", end='', file=sys.stderr)  # Ring the terminal bell

# Run the optimized script
if __name__ == "__main__":
	main()
