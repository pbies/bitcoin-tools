#!/usr/bin/env python3

import json
import base64
import sys
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

INPUT_FILE = "data.txt"
OUTPUT_FILE = "result.txt"

def decrypt_entry(entry, password):
	data_bytes = base64.b64decode(entry["data"])
	iv = base64.b64decode(entry["iv"])
	salt = base64.b64decode(entry["salt"])

	iterations = 10000
	if "keyMetadata" in entry:
		iterations = entry["keyMetadata"].get("params", {}).get("iterations", 10000)

	kdf = PBKDF2HMAC(
		algorithm=hashes.SHA256(),
		length=32,
		salt=salt,
		iterations=iterations,
		backend=default_backend()
	)
	key = kdf.derive(password.encode("utf-8"))

	# AES-256-GCM: last 16 bytes are auth tag
	ciphertext = data_bytes[:-16]
	tag = data_bytes[-16:]

	aesgcm = AESGCM(key)
	plaintext = aesgcm.decrypt(iv, ciphertext + tag, None)
	return plaintext.decode("utf-8")

def main():
	if len(sys.argv) < 2:
		print("Usage: mm_decrypt.py <password>")
		sys.exit(1)

	password = sys.argv[1]

	with open(INPUT_FILE, "r") as f:
		lines = [l.strip() for l in f if l.strip()]

	entries = []
	for line in lines:
		try:
			entries.append(json.loads(line))
		except json.JSONDecodeError:
			continue

	success = 0
	fail = 0

	with open(OUTPUT_FILE, "a") as out:
		for i, entry in enumerate(entries):
			try:
				result = decrypt_entry(entry, password)
				line_out = f"[{i}] OK: {result}"
				print(line_out)
				out.write(line_out + "\n")
				success += 1
			except Exception as e:
				line_out = f"[{i}] FAIL: {e}"
				print(line_out)
				out.write(line_out + "\n")
				fail += 1

	print(f"\nTotal: {len(entries)} | OK: {success} | FAIL: {fail}")
	print(f"Results appended to {OUTPUT_FILE}")

if __name__ == "__main__":
	main()
