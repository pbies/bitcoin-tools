#!/usr/bin/env python3

import base58
import hashlib
import sys

def b58(hex):
    return base58.b58encode_check(hex)

def sha256(hex):
    return hashlib.sha256(hex).digest()

with open("output.txt","w") as f:
    for a in range(256):
        for b in range(256):
            for c in range(256):
                k=sha256(bytearray([a,b,c]))
                extend = '80' + k.hex()
                f.write(b58(bytes.fromhex(extend)).decode('utf-8') + " 0\n")
f.close()
