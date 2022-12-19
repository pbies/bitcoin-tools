#!/usr/bin/env python3

import base58
import hashlib
import sys

def b58(str):
    return base58.b58decode_check(str)
    # hex returned

def main():
    print(b58('5Hpa12RyRz9FM2uT724ACZabuV4eDD6cjiGBz4LCwiKQm5oWWim').hex())
    print(b58('5KZZZZpzUEG3CAwV59XwDd3LSr2kSu8f9SBVAkKKSoA5nQKtm4A').hex())

if __name__ == '__main__':
    main()
