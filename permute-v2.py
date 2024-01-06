#!/usr/bin/env python3

import itertools

words = ['word1', 'word2', 'word3', 'word4', 'word5', 'word6', 'word7', 'word8', 'word9', 'word10', 'word11', 'word12']
permutations = list(itertools.permutations(words))

print(f'Total number of permutations: {len(permutations)}')
