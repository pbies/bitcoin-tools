#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm import tqdm
import base58
import sys
from tqdm.contrib.concurrent import process_map

hdwallet = HDWallet(symbol=BTC)

def pvk_to_wif(key_bytes): # in: b'\x00\x00\x00\x00... [32] out: b'5HpH...
	return base58.b58encode_check(b'\x80' + key_bytes)

def pvk_to_wif2(key_hex): # in: '0000... [64] out: b'5HpH...
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex))

def go(k):
	k=k.strip()
	try:
		hdwallet.from_mnemonic(mnemonic=k)
		tmp1=hdwallet
	except:
		tmp1=None
	try:
		hdwallet.from_private_key(private_key=k)
		tmp2=hdwallet
	except:
		tmp2=None
	try:
		hdwallet.from_seed(seed=k)
		tmp3=hdwallet
	except:
		tmp3=None
	try:
		hdwallet.from_wif(wif=k)
		tmp4=hdwallet
	except:
		tmp4=None
	try:
		hdwallet.from_xprivate_key(xprivate_key=k)
		tmp5=hdwallet
	except:
		tmp5=None
	try:
		hdwallet.from_entropy(entropy=k)
		tmp6=hdwallet
	except:
		tmp6=None
	try:
		k=base58.b58decode_check(k)[0:].hex()[2:]
		hdwallet.from_private_key(private_key=k)
		tmp7=hdwallet
	except:
		tmp7=None

	for i in [tmp1, tmp2, tmp3, tmp4, tmp5, tmp6, tmp7]:
		if i!=None:
			pvk=i.private_key()
			wif=pvk_to_wif2(pvk).decode()
			outfile.write(wif+'\n')
			outfile.write(i.wif()+'\n')
			outfile.write(i.p2pkh_address()+'\n')
			outfile.write(i.p2sh_address()+'\n')
			outfile.write(i.p2wpkh_address()+'\n')
			outfile.write(i.p2wpkh_in_p2sh_address()+'\n')
			outfile.write(i.p2wsh_address()+'\n')
			outfile.write(i.p2wsh_in_p2sh_address()+'\n\n')
			outfile.flush()

infile = open('input.txt','r')
outfile = open('output.txt','w')

lines = infile.readlines()
lines = [x.strip() for x in lines]

process_map(go, lines, max_workers=12, chunksize=1000)

print('\a',end='',file=sys.stderr)
