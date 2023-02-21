#!/usr/bin/env python3

# empty brainwallet phrase to WIF

import base58
import hashlib

key=b''
sha=hashlib.sha256(key).digest()
tmp=b'\x80'+sha
result_priv=base58.b58encode_check(tmp)
print(result_priv.decode('utf-8'))
