#!/usr/bin/env python3
from cryptotools import PrivateKey
import sys

prv = PrivateKey.from_wif(sys.argv[1])
print(prv.hex())
