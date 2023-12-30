#!/usr/bin/env python3

import sys
import struct
import json
import binascii

txid="4e9e28b2e7d9b28824ab19f02ace19dff86aed90d8fb422c640279a6fe82e0af"
vout=0
pubkey="02396543d7ab32e75c6682b4fca35c0e68f0694b0dde355de5cc2a7f8fa4affc62"
amount=0.067

tx = bytearray()
tx = tx + binascii.unhexlify('0100000001') # one input tx - last digit
txb = bytes.fromhex(txid)
seqno = 1
txb=txb[::-1]
tx = tx + bytes(txb)
tx = tx + struct.pack('<I',vout)
tx = tx + b'\x00'
tx = tx + struct.pack('<i',seqno)
tx = tx + bytes([1]) # ?
pk = pubkey
v = amount
if len(pk) != 66:
    raise ValueError("pk not 33 bytes (66 hex digits) - it has bytes: "+str(len(pk)/2))
v = int(100000000 * v)
tx = tx + struct.pack('<Q',v)
tx = tx + b'\x23'
tx = tx + b'\x21'
tx = tx + binascii.unhexlify(pk)
tx = tx + b'\xac'
tx = tx + binascii.unhexlify('00000000')
print(binascii.hexlify(tx).decode('ascii'))
