#!/usr/bin/env python3

import itertools
from bip_utils import Bip39SeedGenerator, Bip39MnemonicValidator, Bip39WordsNum

wordlist = open('english.txt','r').read().splitlines()

words_num=12

for combination in itertools.product(wordlist, repeat=words_num):
	mnemonic = " ".join(combination)
	if Bip39MnemonicValidator().IsValid(mnemonic):
		print(mnemonic)
