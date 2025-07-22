#!/usr/bin/env python3

import subprocess
from pathlib import Path

wallets = Path('.').glob('*')

for wallet in wallets:
	try:
		# Get addresses first
		addr_cmd = [
			"electrum",
			"-w", "./"+str(wallet),
			"listaddresses",
			"--offline"
		]
		addr_result = subprocess.run(addr_cmd, capture_output=True, text=True)
		addresses = eval(addr_result.stdout)  # Careful with eval in production

		print(f"Private keys for wallet: {wallet}")
		for address in addresses:
			pk_cmd = [
				"electrum",
				"--wallet", "./"+str(wallet),
				"getprivatekeys", address,
				"--offline"
			]
			pk_result = subprocess.run(pk_cmd, capture_output=True, text=True)
			print(f"{address}: {pk_result.stdout.strip()}")
	except Exception as e:
		print(f"Error with wallet {wallet}: {e}")
