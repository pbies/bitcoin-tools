#!/usr/bin/env python3

# convert 32-bytes of private key to public address and WIF

import base58
import hashlib
from bitcoin import *

f=open('input.bin','rb')
privkey=bytearray(f.read(32))

print('pub: '+pubtoaddr(privkey))

sha=hashlib.sha256(privkey).digest()
tmp=b'\x80'+sha
result_priv=base58.b58encode_check(tmp)
print('wif: '+result_priv.decode('utf-8'))
