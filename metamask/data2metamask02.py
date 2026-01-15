#!/usr/bin/env python3

import json
import base64
import sys
import os

HASHCAT_MODE = 26600  # MetaMask Wallet


def b64_validate(value: str) -> str:
	value = value.strip()
	base64.b64decode(value, validate=True)
	return value


def parse_single_metamask_wallet(wallet):
	try:
		if isinstance(wallet, str):
			wallet = json.loads(wallet)

		cipher_data = wallet.get("data")
		iv = wallet.get("iv")

		salt = wallet.get("salt")
		if not salt:
			salt = wallet.get("params", {}).get("salt")
		if not salt:
			salt = wallet.get("keyMetadata", {}).get("params", {}).get("salt")

		if not cipher_data or not iv or not salt:
			return None, "missing required fields (need: data, iv, salt)"

		cipher_data = b64_validate(cipher_data)
		iv = b64_validate(iv)
		salt = b64_validate(salt)

		# Hashcat -m 26600 format:
		# $metamask$<BASE64_salt>$<BASE64_iv>$<BASE64_data>
		hashcat_hash = f"$metamask${salt}${iv}${cipher_data}"
		return hashcat_hash, "ok"

	except Exception as e:
		return None, str(e)


def process_json_file(input_file, output_file):
	with open(input_file, "r", encoding="utf-8") as f:
		content = f.read().strip()

	wallets = []

	try:
		obj = json.loads(content)
		if isinstance(obj, list):
			wallets = obj
		else:
			wallets = [obj]
	except json.JSONDecodeError:
		for line in content.splitlines():
			line = line.strip()
			if not line:
				continue
			wallets.append(json.loads(line))

	ok = []
	fail = []

	for i, w in enumerate(wallets, 1):
		h, err = parse_single_metamask_wallet(w)
		if h:
			ok.append(h)
		else:
			fail.append((i, err))

	with open(output_file, "w", encoding="utf-8") as f:
		for h in ok:
			f.write(h + "\n")

	print(f"wallets: {len(wallets)}")
	print(f"ok: {len(ok)}")
	print(f"fail: {len(fail)}")
	print(f"output: {output_file}")

	if fail:
		for idx, err in fail[:10]:
			print(f"fail[{idx}]: {err}")
		if len(fail) > 10:
			print(f"... and {len(fail) - 10} more")

	return ok, fail


def main():
	if len(sys.argv) < 2:
		print(f"usage: {sys.argv[0]} input.json [output.txt]")
		sys.exit(1)

	input_file = sys.argv[1]
	if not os.path.exists(input_file):
		print(f"error: input file not found: {input_file}")
		sys.exit(1)

	output_file = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(input_file)[0] + "_hashes_26600.txt"

	process_json_file(input_file, output_file)

	print("\nhashcat:")
	print(f"hashcat -m {HASHCAT_MODE} {output_file} wordlist.txt")


if __name__ == "__main__":
	main()
