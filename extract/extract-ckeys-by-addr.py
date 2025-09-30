#!/usr/bin/env python3

from bitcoin.wallet import CBitcoinSecret, P2PKHBitcoinAddress
import os

# Replace "wallet.dat" with the path to your Bitcoin Core wallet file
wallet_file = "wallet.dat"

# Replace "bitcoinaddress" with the address you want to extract the ckey for
address = "bitcoinaddress"

# Open and read the wallet file
with open(wallet_file, "rb") as f:
    wallet_data = f.read()

# Search for the key associated with the specified address and extract the private key value
ckey = None
for i in range(len(wallet_data)):
    if wallet_data[i:i+21] == b"\x76\xa9\x14" and wallet_data[i+21:i+25] == P2PKHBitcoinAddress(address).to_bytes():
        j = i + 25
        while wallet_data[j] != 0xbc:
            j += 1
        ckey = CBitcoinSecret.from_secret_bytes(wallet_data[j+1:j+34]).hex()
        break

# Print the ckey, if found
if ckey:
    print("Ckey:", ckey)
else:
    print("Ckey not found.")
