#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
from tqdm import tqdm
import base58
import sys
from tqdm.contrib.concurrent import process_map

hdwallet = HDWallet(symbol=BTC)

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

known="dinner work badge avocado object blanket together jar early mass "

d=open('english.txt','r').read().splitlines()

outfile=open('output.txt','w')

for i in d:
	for j in d:
		check=known+i+' '+j
		try:
			hdwallet.from_mnemonic(mnemonic=check)
		except:
			continue
		pvk=hdwallet.private_key()
		wif=pvk_to_wif2(pvk)
		outfile.write(check+'\n'+wif+'\n'+hdwallet.wif()+'\n'+hdwallet.p2pkh_address()+'\n'+hdwallet.p2sh_address()+'\n'+hdwallet.p2wpkh_address()+'\n'+hdwallet.p2wpkh_in_p2sh_address()+'\n'+hdwallet.p2wsh_address()+'\n'+hdwallet.p2wsh_in_p2sh_address()+'\n\n')
		outfile.flush()

print('\a', end='', file=sys.stderr)
