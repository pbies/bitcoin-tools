#!/usr/bin/env python3

# (C) 2024 Aftermath @Tzeeck

import base58
import binascii
import ecdsa
import hashlib
import requests

from pprint import pprint

from hdwallet import HDWallet
from hdwallet.symbols import BTC

#from cryptos import *

def int_to_hex(i): # in: int out: 0x8000
	return hex(i)

def hex_to_int(hex): # in: '8000... out: 32768
	return int(hex, 16)

def getWif(privkey):
	wif = b"\x80" + privkey
	wif = base58.b58encode_check(wif + sha256(sha256(wif))[:4])
	return wif.decode()

def sha256(data):
	digest = hashlib.new("sha256")
	digest.update(data)
	return digest.digest()

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex))

pvk=input('Enter int or hex pvk to check (without 0x): ')

i=0
h=''

try:
	i=int(pvk)
	h=int_to_hex(i)[2:]
	print('Detected int')
except:
	try:
		h=pvk
		i=hex_to_int(pvk)
		print('Detected hex')
	except:
		print('Error detecting pvk!')
		exit(1)

h='0'*(64-len(h))+h
byt=bytes.fromhex(h)

hdwallet = HDWallet(symbol=BTC)
hdwallet.from_private_key(private_key=h)
d=hdwallet.dumps()

pubkey=d['compressed']
pubkeyun=d['uncompressed']
addrco=d['addresses']['p2pkh']
addrunco=d['addresses']['p2sh']

r=requests.get('https://blockchain.info/q/addressbalance/'+addrco)
if not r.status_code==200:
	print('Error',r.status_code)
	exit(1)

q=requests.get('https://blockchain.info/q/addressbalance/'+addrunco)
if not q.status_code==200:
	print('Error',q.status_code)
	exit(1)

b=int(r.text)
c=int(q.text)

print('pvk hex: '+h)
print('\naddress compressed b58c: '+addrco)
print('\naddress uncompressed b58c: '+addrunco)
print('\npubkey (don\'t share!) compressed hex:\n'+pubkey)
print('\npubkey (don\'t share!) uncompressed hex:\n'+pubkeyun)
print('\nWIF compressed (don\'t share!) b58c: '+d['wif'])
print('\nWIF uncompressed (don\'t share!) b58c: '+pvk_to_wif2(h).decode())
print(f'\nbalance ({addrco}):')
print(r.text,'sat')
print(b/100000,'mBTC')
print(b/100000000,'BTC')
print(f'\nbalance ({addrunco}):')
print(q.text,'sat')
print(c/100000,'mBTC')
print(c/100000000,'BTC')
print()
