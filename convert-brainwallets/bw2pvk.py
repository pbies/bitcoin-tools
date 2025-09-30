#!/usr/bin/env python3

import hashlib

def brainwallet_to_private_key(passphrase):
    # Use SHA-256 to hash the passphrase
    private_key = hashlib.sha256(passphrase.encode('utf-8')).hexdigest()
    return private_key
