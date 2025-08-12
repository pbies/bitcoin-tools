#!/usr/bin/env python3

import datetime
import ecdsa
import hashlib
import os
import random
import secrets
import time

def sha256(data):
	return hashlib.sha256(data).digest()

def ripemd160(data):
	h = hashlib.new('ripemd160')
	h.update(data)
	return h.digest()


def generate_random_private_key() -> str:
	return secrets.randbelow(0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364140)

def pvk_to_pubkey(hex_key):
	try:
		sk = ecdsa.SigningKey.from_string(bytes.fromhex(hex_key), curve=ecdsa.SECP256k1)
		return (b'\x04' + sk.verifying_key.to_string()).hex()
	except Exception as e:
		log(f'Error generating public key: {e}')
		return None

def log(message):
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	with open('log.txt', 'a') as log_file:
		log_file.write(f'{timestamp} {message}\n')
	print(f'{timestamp} {message}', flush=True)

class Node:
	def __init__(self, data):
		self.left = None
		self.right = None
		self.data = data

	def insert(self, data):
		if self.data:
			if data < self.data:
				if self.left is None:
					self.left = Node(data)
				else:
					self.left.insert(data)
			elif data > self.data:
					if self.right is None:
						self.right = Node(data)
					else:
						self.right.insert(data)
		else:
			self.data = data

def buildTree(addrs, start, end):
	if (start > end):
		return None

	mid = int(start + (end - start) / 2)
	node = Node(addrs[mid])

	node.left = buildTree(addrs, start, mid - 1)
	node.right = buildTree(addrs, mid + 1, end)

	return node

def search(root, key):
	if root is None or root.data == key:
		return root

	if root.data < key:
		return search(root.right, key)

	return search(root.left, key)

def main():
	print("Bitcoin Private Key Scanner Demo (C) 2025 Aftermath @Tzeeck")
	print("Scanning random addresses in an infinite loop. Press Ctrl+C to stop.\n")

	with open('pubkeys.txt') as f:
		pubkeys = f.read().splitlines()

	tree = buildTree(pubkeys, 0, len(pubkeys) - 1)

	keys_checked = 0
	start_time = time.time()
	CNT=256

	try:
		while True:
			private_key = generate_random_private_key()
			for i in range(private_key, private_key+CNT):
				j=hex(i)[2:].zfill(64)
				pubkey = pvk_to_pubkey(j)
			
				if pubkey and search(tree, pubkey):
					log(f'Found matching private key: {j}')

			keys_checked += CNT

			if keys_checked % (CNT*8) == 0:
				elapsed = time.time() - start_time
				rate = keys_checked / elapsed
				print(f"\rKeys checked: {keys_checked:,} | "
					  f"Rate: {rate:.2f} keys/sec", end='', flush=True)

	except KeyboardInterrupt:
		print("\n\nScanning stopped by user.")
		print(f"Total keys checked: {keys_checked:,}")

if __name__ == "__main__":
	main()
