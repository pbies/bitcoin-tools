#!/usr/bin/env python3

# hex convert to public/private key in format base58

import base58
import hashlib
import sys

def b58(hex):
    return base58.b58encode_check(hex)

def main():
    with open("input.txt") as f:
        content = f.readlines()

    content = [x.strip() for x in content]

    o = open('output.txt','w')

    for line in content:
        s1=bytearray.fromhex(line)
        o.write(b58(s1).decode('ascii') + "\n")

if __name__ == '__main__':
    main()
