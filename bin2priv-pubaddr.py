#!/usr/bin/env python3

import base58
import ecdsa
import hashlib

f=open('input.bin','rb')
Private_key=bytearray(f.read(32))
signing_key = ecdsa.SigningKey.from_string(Private_key, curve = ecdsa.SECP256k1)
verifying_key = signing_key.get_verifying_key()
public_key = b"\x04" + verifying_key.to_string()
sha256_1 = hashlib.sha256(public_key)
ripemd160 = hashlib.new("ripemd160")
ripemd160.update(sha256_1.digest())
hashed_public_key = b"\x00" + ripemd160.digest()
checksum_full = hashlib.sha256(hashlib.sha256(hashed_public_key).digest()).digest()
checksum = checksum_full[:4]
bin_addr = hashed_public_key + checksum
result_address = base58.b58encode(bin_addr).decode('utf-8')
print('pub: '+result_address)
sha=hashlib.sha256(Private_key).digest()
tmp=b'\x80'+sha
result_priv=base58.b58encode_check(tmp)
print('wif: '+result_priv.decode('utf-8'))
