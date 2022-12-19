#!/usr/bin/env python3

import base58
import hashlib
import sys

def b58(str):
    return base58.b58decode_check(str)
    # hex returned



def main():
    print(b58('5HpHagT65TZzG1PH3CSu63k8DbpvD8s5ip4nEB3kEsreAnchuDf').hex())
    print(b58('5HpHagT65TZzG1PH3CSu63k8DbpvD8s5ip4nEB3kEsreAvUcVfH').hex())

if __name__ == '__main__':
    main()
