#!/usr/bin/env python3

from mnemonic import Mnemonic
from tqdm import tqdm
import base58
import binascii

mnemonic=Mnemonic("english")

i='seeds.txt'
cnt=sum(1 for line in open(i))
o=open('output.txt','w')

for seed in tqdm(open(i,'r'),total=cnt):
	seed=seed.strip()
	xprv = mnemonic.to_hd_master_key(binascii.unhexlify(seed))
	pvk = base58.b58decode_check(xprv)[-32:]
	o.write('0x'+pvk.hex()+'\n')
