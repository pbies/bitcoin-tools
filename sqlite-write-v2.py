#!/usr/bin/env python3

import base58
import ecdsa
import hashlib
import os
import sqlite3

conn = sqlite3.connect("bitcoin_keys.db")
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS keys (private_key TEXT, public_key TEXT, address TEXT)")

for i in range(100000):
	private_key = os.urandom(32)
	signing_key = ecdsa.SigningKey.from_string(private_key, curve = ecdsa.SECP256k1)
	verifying_key = signing_key.get_verifying_key()
	public_key = bytes.fromhex("04") + verifying_key.to_string()

	sha256_1 = hashlib.sha256(public_key)

	ripemd160 = hashlib.new("ripemd160")
	ripemd160.update(sha256_1.digest())

	hashed_public_key = bytes.fromhex("00") + ripemd160.digest()
	checksum_full = hashlib.sha256(hashlib.sha256(hashed_public_key).digest()).digest()
	checksum = checksum_full[:4]
	bin_addr = hashed_public_key + checksum

	result_address = base58.b58encode(bin_addr)

	cursor.execute("INSERT INTO keys VALUES (?, ?, ?)", (private_key, public_key, result_address))

conn.commit()
conn.close()

print("Keys generated and written to database.")
