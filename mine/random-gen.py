#!/usr/bin/env python3

import ssl
import random
import os

print(hex(random.SystemRandom().getrandbits(256)))
print(f'0x{os.urandom(32).hex()}')
print(f'0x{ssl.RAND_bytes(32).hex()}')
