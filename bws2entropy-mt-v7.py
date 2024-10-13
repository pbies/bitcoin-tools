#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm.contrib.concurrent import process_map
from tqdm import tqdm
import sys, hashlib, base58

# Global HDWallet object
hdwallet = HDWallet(symbol=BTC)

# Helper function to compute SHA-256 hash
def sha(x):
	t1 = hashlib.sha256()
	t1.update(x)
	return t1.digest()

# Helper function to compute SHA-256 hash and return in hex format
def shahex(x):
	t1 = hashlib.sha256()
	t1.update(x)
	return t1.hexdigest()

# Function to convert private key in hex format to Wallet Import Format (WIF)
def pvk_to_wif2(key_hex):
	b = bytes.fromhex(key_hex)
	t1 = b'\x80' + b
	w = base58.b58encode_check(t1)
	return w

# Optimized processing function for each line
def go(k):
	s1 = shahex(k)
	s2 = shahex(sha(k))
	d1, d2, d3, d4 = s1[:32], s1[32:64], s2[:32], s2[32:64]

	# Collecting output strings in a list to write them at once
	output_lines = []

	# Process entropy parts d1 and d2
	for entropy in (d1, d2, d3, d4):
		hdwallet.from_entropy(entropy=entropy)
		pvk = hdwallet.private_key()
		wif = pvk_to_wif2(pvk).decode()
		
		output_lines.append(wif + '\n')
		output_lines.append(hdwallet.wif() + '\n')
		output_lines.append(hdwallet.p2pkh_address() + '\n')
		output_lines.append(hdwallet.p2sh_address() + '\n')
		output_lines.append(hdwallet.p2wpkh_address() + '\n')
		output_lines.append(hdwallet.p2wpkh_in_p2sh_address() + '\n')
		output_lines.append(hdwallet.p2wsh_address() + '\n')
		output_lines.append(hdwallet.p2wsh_in_p2sh_address() + '\n\n')

	# Write all collected lines at once (reduces I/O operations)
	outfile.write("".join(output_lines))
	outfile.flush()

# Read the input file
print('Reading...', flush=True)
with open('input.txt', 'rb') as infile:
	lines = infile.read().splitlines()

# Open the output file with buffered writes
print('Writing...', flush=True)
with open('output.txt', 'w') as outfile:
	# Use parallel processing for the 'go' function
	process_map(go, lines, max_workers=24, chunksize=1000)

# Signal completion
print('\a', end='', file=sys.stderr)
