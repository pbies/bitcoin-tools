#!/usr/bin/env python3

import hashlib

def bip39_is_checksum_valid(mnemonic: str) -> bool:
	words = mnemonic
	words_len = len(words)
	with open('english.txt') as f:
		wordlist = [line.strip() for line in f]
	n = len(wordlist)
	i = 0
	words.reverse()
	while words:
		w = words.pop()
		try:
			k = wordlist.index(w)
		except ValueError:
			return False, False
		i = i*n + k
	if words_len not in [12, 15, 18, 21, 24]:
		return False
	checksum_length = 11 * words_len // 33  # num bits
	entropy_length = 32 * checksum_length  # num bits
	entropy = i >> checksum_length
	checksum = i % 2**checksum_length
	entropy_bytes = int.to_bytes(entropy, length=entropy_length//8, byteorder="big")
	sha=hashlib.sha256()
	sha.update(entropy_bytes)
	hash=sha.digest()
	hashed = int.from_bytes(hash, byteorder="big")
	calculated_checksum = hashed >> (256 - checksum_length)
	return checksum == calculated_checksum

import sys

m=sys.argv[1:]

if bip39_is_checksum_valid(m)==True:
	print('Valid!')
	exit(0)
else:
	print('Invalid!')
	exit(1)
