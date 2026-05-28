#!/usr/bin/env python3

import os
import sys
import glob

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Bitcoin Core stores the master encryption key under the serialized key b'\x04mkey'.
# Present = wallet is encrypted. Absent = wallet is plain/unencrypted.
MKEY = b'\x04mkey'

def is_encrypted(path):
	try:
		with open(path, 'rb') as f:
			return MKEY in f.read()
	except OSError as e:
		return e

patterns = ['wallet.dat', '*.dat', '*.sqlite', '*.db']
seen = set()
wallets = []
for p in patterns:
	for f in glob.glob(p):
		if os.path.isfile(f) and f not in seen:
			seen.add(f)
			wallets.append(f)
wallets.sort()

if not wallets:
	print('No wallet files found in current directory.')
	sys.exit(0)

print('Checking ' + str(len(wallets)) + ' file(s)...')
print('')

plain = []
errors = []
for w in wallets:
	result = is_encrypted(w)
	if isinstance(result, Exception):
		errors.append((w, str(result)))
	elif not result:
		plain.append(w)

if plain:
	print('PLAIN (unencrypted):')
	for w in plain:
		print('  ' + w)
else:
	print('No plain wallets found - all appear encrypted.')

if errors:
	print('')
	print('Errors:')
	for w, e in errors:
		print('  ' + w + ': ' + e)
