#!/usr/bin/env python3

# BCH m/44/145
# BTC m/84/0/0/0
# ETH m/44/60
# LTC m/84/2

import pprint
import binascii
import mnemonic
import bip32utils
import hashlib
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

def sha256hex(h):
	return hashlib.sha256(h).hexdigest()

def bytes_to_string(bytes): # in: b'abc1... out: abc1...
	return bytes.decode('utf-8')

def bip39(seed,x,y):
	bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed)
	bip32_child_key_obj = bip32_root_key_obj.ChildKey(
		84 + bip32utils.BIP32_HARDEN
	).ChildKey(
		0 + bip32utils.BIP32_HARDEN
	).ChildKey(
		0 + bip32utils.BIP32_HARDEN
	).ChildKey(x).ChildKey(y)

	return bip32_child_key_obj.WalletImportFormat()

i = open('input.txt','rb')
o = open('output.txt','w')

print('Loading...')
lines = i.readlines()

lines = [x.strip() for x in lines]

cnt=len(lines)

c=0
print('Running conversion...')

for z in lines:
	for x in range(9):
		for y in range(9):
			#print(str(x)+' '+str(y),flush=True)
			t=bip39(hashlib.sha256(z).digest(),x,y)
			#print(t)
			o.write(t+' 0\n')
			o.flush()
			c=c+1
			print('{:.4f}%'.format(c/cnt),end='\r')

#process_map(go, lines, max_workers=4, chunksize=10)
i.close()
o.close()
print('Sorting...')
o1=open('output.txt','r')
o2=open('output2.txt','w')
f1=o1.readlines()
s1=set(f1)
s2=list(s1)
s2.sort()
o2.writelines(s2)
print('Done!')
