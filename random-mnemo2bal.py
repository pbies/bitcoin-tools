#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet
# pip3 install bip_utils

from bip_utils import Bip39MnemonicGenerator, Bip39SeedGenerator, Bip39WordsNum, Bip44, Bip44Changes, Bip44Coins
from hdwallet import HDWallet
from hdwallet.symbols import BTC
from urllib.request import urlopen
import json
import os
import requests

hdwallet = HDWallet(symbol=BTC)

def check_bal(address):
	try:
		htmlfile = urlopen("https://mempool.space/api/address/%s" % address, timeout = 20)
	except:
		return None
	else: 
		res = json.loads(htmlfile.read())
		funded=res['chain_stats']['funded_txo_sum']
		spent=res['chain_stats']['spent_txo_sum']
		bal=funded-spent
		return bal

for i in range(0,100):
	m = Bip39MnemonicGenerator().FromWordsNumber(Bip39WordsNum.WORDS_NUM_12)
	m2 = m.ToStr()
	print('mnemo: '+m2)
	hdwallet.from_mnemonic(mnemonic=m2)
	print('WIF: '+hdwallet.wif())
	b1=str(check_bal(hdwallet.p2pkh_address()))
	print('private_key: '+hdwallet.private_key())
	print('p2pkh: '+hdwallet.p2pkh_address()+' : '+b1)
	b2=str(check_bal(hdwallet.p2sh_address()))
	print('p2sh: '+hdwallet.p2sh_address()+' : '+b2)
	b3=str(check_bal(hdwallet.p2wpkh_address()))
	print('p2wpkh: '+hdwallet.p2wpkh_address()+' : '+b3)
	b4=str(check_bal(hdwallet.p2wpkh_in_p2sh_address()))
	print('p2wpkh_in_p2sh: '+hdwallet.p2wpkh_in_p2sh_address()+' : '+b4)
	b5=str(check_bal(hdwallet.p2wsh_address()))
	print('p2wsh: '+hdwallet.p2wsh_address()+' : '+b5)
	b6=str(check_bal(hdwallet.p2wsh_in_p2sh_address()))
	print('p2wsh_in_p2sh: '+hdwallet.p2wsh_in_p2sh_address()+' : '+b6+'\n')

import sys
print('\a',end='',file=sys.stderr)
