#!/usr/bin/env python3

import hashlib
import base58
import binascii

private_key_WIF = input("WIF: ")
first_encode = base58.b58decode(private_key_WIF)
private_key_full = binascii.hexlify(first_encode)
private_key = private_key_full[2:-8]
print(bytes.fromhex(private_key.decode('utf-8')))
