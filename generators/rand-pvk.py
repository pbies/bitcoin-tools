#!/usr/bin/env python3

def randpvk1():
	import secrets
	return secrets.token_hex(32)

def randpvk2():
	import os
	return os.urandom(32).hex()

def randpvk3():
	import os
	import binascii
	return binascii.hexlify(os.urandom(32)).decode("ascii")

def randpvk4():
	import random
	return f"{random.getrandbits(256):064x}"

print(randpvk1())
print(randpvk2())
print(randpvk3())
print(randpvk4())
