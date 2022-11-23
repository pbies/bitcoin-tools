#!/usr/bin/env python3

import base58
import hashlib
from bitcoin import *
import binascii

key=b''
sha=sha256(key)
tmp=binascii.unhexlify('80'+sha)
result_priv=base58.b58encode_check(tmp)
print(result_priv.decode('utf-8'))
