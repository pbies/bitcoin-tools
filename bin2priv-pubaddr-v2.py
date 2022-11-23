#!/usr/bin/env python3

import bitcoin
import sys

pk=sys.argv[1]
print('pub: '+bitcoin.privtoaddr(pk))
