#!/usr/bin/env python3
# private hex bitcoin btc key to wif wallet import format
import base58
import hashlib
import sys

def b58(hex):
    return base58.b58encode_check(hex)

def sha256(hex):
    return hashlib.sha256(hex).digest()

def main():
    for y in range(55296):
            k = sha256(chr(y).encode())
            extend = '80' + k.hex()
            print(b58(bytes.fromhex(extend)).decode('utf-8'))
            #print(chr(y),end='')

if __name__ == '__main__':
    main()
