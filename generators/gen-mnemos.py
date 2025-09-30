#!/usr/bin/env python3

import itertools
from bip_utils import Bip39SeedGenerator, Bip39MnemonicValidator, Bip39WordsNum

# Example reduced list of words (just for demonstration)
wordlist = open('english.txt','r').read().splitlines()

# Brute-force all possible combinations (DO NOT use with the full 2048-word list)
def brute_force_mnemonics(wordlist, words_num=12):
	for combination in itertools.product(wordlist, repeat=words_num):
		mnemonic = " ".join(combination)
		if Bip39MnemonicValidator().IsValid(mnemonic):
			print(f"Valid mnemonic found: {mnemonic}")
			break

if __name__ == "__main__":
	# This would be the starting point of the brute-force process
	brute_force_mnemonics(wordlist)
