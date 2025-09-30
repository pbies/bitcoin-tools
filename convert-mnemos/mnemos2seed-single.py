#!/usr/bin/env python3

from mnemonic import Mnemonic
import sys

mnemo = Mnemonic("english")

# param 1 = words in ""
# param 2 = password (empty = "")

print(mnemo.to_seed(sys.argv[1], sys.argv[2]).hex())
