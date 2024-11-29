#!/usr/bin/env python3

from hdwallet import HDWallet
from hdwallet.symbols import BTC
import itertools
from bip_utils import Bip39SeedGenerator, Bip39MnemonicValidator, Bip39WordsNum
import sys, base58
from tqdm.contrib.concurrent import process_map

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex)).decode()

wordlist = open('english.txt','r').read().splitlines()
outfile = open('output.txt','w')

hdwallet = HDWallet(symbol=BTC)

words_num=2
known="dinner work badge avocado object blanket together jar early mass "

def go(combination):
	mnemonic = known+" ".join(combination)
	try:
		hdwallet.from_mnemonic(mnemonic=mnemonic)
	except:
		return
	pvk=hdwallet.private_key()
	wif=pvk_to_wif2(pvk)
	outfile.write(mnemonic+'\n'+wif+'\n'+hdwallet.wif()+'\n'+hdwallet.p2pkh_address()+'\n'+hdwallet.p2sh_address()+'\n'+hdwallet.p2wpkh_address()+'\n'+hdwallet.p2wpkh_in_p2sh_address()+'\n'+hdwallet.p2wsh_address()+'\n'+hdwallet.p2wsh_in_p2sh_address()+'\n\n')
	outfile.flush()

process_map(go, itertools.product(wordlist, repeat=words_num), max_workers=16, chunksize=1000)

print('\a', end='', file=sys.stderr)
