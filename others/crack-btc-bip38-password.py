#!/usr/bin/env python3

# pip uninstall pycryptodome
# pip install pycrypto

import hashlib
import pybip38
import sys

BIP38 = '6PnQmAyBky9ZXJyZBv9QSGRUXkKh9HfnVsZWPn4YtcwoKy5vufUgfA3Ld7'

for line in open('passwords.txt','r',encoding='utf-8'):
    passwords = []
    password = line.strip()
    md5 =  hashlib.md5(str.encode(password)).hexdigest()
    sha512 =  hashlib.sha512(str.encode(password)).hexdigest()
    sha256 =  hashlib.sha256(str.encode(password)).hexdigest()
    passwords.append(str(password))
    passwords.append(str(password) + str(password))
    passwords.append(str(md5))
    passwords.append(str(md5) + str(md5))
    passwords.append(str(sha512))
    passwords.append(str(sha512) + str(sha512))
    passwords.append(str(sha256))
    passwords.append(str(sha256) + str(sha256))

    for item in passwords:
        print('.',end='',flush=True)
        #print("# Trying password: %s" % item)
        if pybip38.bip38decrypt(item, BIP38) != False:
            print("\n## KEY FOUND: %s\n" % item)
            sys.exit(0)

print("\n## Password NOT found :-(\n")
