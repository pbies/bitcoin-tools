#!/usr/bin/env python3

import hashlib
import base58

def private_key_to_wif(private_key_hex, compressed=True):
    # Step 1: Add version byte (0x80 for mainnet)
    version_byte = b'\x80'
    private_key_bytes = bytes.fromhex(private_key_hex)
    
    if compressed:
        private_key_bytes += b'\x01'  # Add compression flag
    
    extended_key = version_byte + private_key_bytes
    
    # Step 2: Double SHA-256 hash for checksum
    checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]
    
    # Step 3: Concatenate extended key and checksum
    final_key = extended_key + checksum
    
    # Step 4: Encode in Base58
    wif = base58.b58encode(final_key).decode('utf-8')
    return wif

# Example usage
passphrase = "your passphrase"
private_key = brainwallet_to_private_key(passphrase)
wif_key = private_key_to_wif(private_key)
print(f"WIF: {wif_key}")
