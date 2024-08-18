#!/usr/bin/env python3

def hex_to_b58c(h):
	return base58.b58encode_check(bytes.fromhex(h)).decode()

def int_to_b58c_wif(b):
	return base58.b58encode_check(b'\x80'+b.to_bytes(32,'big')).decode()
