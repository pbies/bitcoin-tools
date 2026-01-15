#!/usr/bin/env python3

import json
import base64
import sys
import os

HASHCAT_MODE = 16300  # MetaMask / PBKDF2-SHA256
DEFAULT_ITERATIONS = 600000


def b64_validate(value: str) -> str:
	value = value.strip()
	base64.b64decode(value, validate=True)
	return value


def parse_single_metamask_wallet(wallet):
	try:
		if isinstance(wallet, str):
			wallet = json.loads(wallet)

		data = wallet.get("data")
		iv = wallet.get("iv")

		salt = wallet.get("salt")
		if not salt:
			salt = wallet.get("params", {}).get("salt")
		if not salt:
			salt = wallet.get("keyMetadata", {}).get("params", {}).get("salt")

		iterations = (
			wallet.get("params", {}).get("iterations")
			or wallet.get("keyMetadata", {}).get("params", {}).get("iterations")
			or DEFAULT_ITERATIONS
		)

		if not data or not iv or not salt:
			return None, "missing required fields"

		data = b64_validate(data)
		iv = b64_validate(iv)
		salt = b64_validate(salt)

		hashcat_hash = f"$metamask${iterations}${salt}${iv}${data}"
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

	return ok, fail


def main():
	if len(sys.argv) < 2:
		print(f"usage: {sys.argv[0]} input.json [output.txt]")
		sys.exit(1)

	input_file = sys.argv[1]
	output_file = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(input_file)[0] + "_hashes.txt"

	process_json_file(input_file, output_file)

	print("\nhashcat:")
	print(f"hashcat -m {HASHCAT_MODE} {output_file} wordlist.txt")


if __name__ == "__main__":
	main()
