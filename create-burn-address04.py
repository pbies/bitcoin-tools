#!/usr/bin/env python3

"""bitcoin-burn-address-generator.py: This script generates bitcoin coin burning addresses with a custom bitcoin address prefix. 
	The symbols at the end of the burning btc address are made for checksum verification."""

__author__      = "Daniel Gockel"
__website__     = "https://www.10xrecovery.org/"

import sys

from base58 import b58encode, b58decode
from hashlib import sha256

base58_characters = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

bitcoin_address_prefix = "1Piotr"  # should start with 1..., Version prefix (hex) for Bitcoin Address is 0x00

if __name__ == "__main__":
	for char in bitcoin_address_prefix:
		if char not in base58_characters:
			sys.exit("Character '%s' is not a valid base58 character." % char)

	address_length = len(bitcoin_address_prefix)
	if address_length < 34:
		bitcoin_address_prefix = bitcoin_address_prefix + ((34 - address_length) * "X")
	else:
		bitcoin_address_prefix = bitcoin_address_prefix[:34]

	# bitcoin address will have 34 characters from now on

	# decode address
	decoded_address = b58decode(bitcoin_address_prefix)[:-4]  # cut 4 bytes for checksum at the end
	checksum = sha256(sha256(decoded_address).digest()).digest()[:4]
	print("Your Bitcoin burning address is: " + b58encode(decoded_address + checksum).decode("utf-8"))
