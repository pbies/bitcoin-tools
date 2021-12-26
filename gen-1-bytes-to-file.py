#!/usr/bin/env python3

import base58
import hashlib
import sys

o = open('output.txt','wb')

for i in range(256):
    o.write(i.to_bytes(1,byteorder='big'));
    o.write(b'\x0a');
