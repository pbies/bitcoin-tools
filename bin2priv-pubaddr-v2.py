#!/usr/bin/env python3

# convert private key to public address

import bitcoin
import sys

pk=sys.argv[1]
print('pub: '+bitcoin.privtoaddr(pk))
