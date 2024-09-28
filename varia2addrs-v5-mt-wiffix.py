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
	except:
		try:
			hdwallet.from_private_key(private_key=k)
		except:
			try:
				hdwallet.from_seed(seed=k)
			except:
				try:
					hdwallet.from_wif(wif=k)
				except:
					try:
						hdwallet.from_xprivate_key(xprivate_key=k)
					except:
						try:
							k=base58.b58decode_check(k)[0:].hex()[2:]
							hdwallet.from_private_key(private_key=k)
						except:
							return

	pvk=hdwallet.private_key()
	wif=pvk_to_wif2(pvk).decode()
	outfile.write(wif+'\n')
	outfile.write(hdwallet.wif()+'\n')
	outfile.write(hdwallet.p2pkh_address()+'\n')
	outfile.write(hdwallet.p2sh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_address()+'\n')
	outfile.write(hdwallet.p2wpkh_in_p2sh_address()+'\n')
	outfile.write(hdwallet.p2wsh_address()+'\n')
	outfile.write(hdwallet.p2wsh_in_p2sh_address()+'\n\n')
	outfile.flush()

infile = open('input.txt','r')
outfile = open('output.txt','w')

lines = infile.readlines()
lines = [x.strip() for x in lines]

process_map(go, lines, max_workers=12, chunksize=1000)

print('\a',end='',file=sys.stderr)
