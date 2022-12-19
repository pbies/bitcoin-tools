#!/usr/bin/python

import binascii
import os
import hashlib
import sys
import base58

# bytes to read at a time from file (10meg)
readlength=10*1024*1024

magic = '\x01\x30\x82\x01\x13\x02\x01\x01\x04\x20'
magiclen = len(magic)

def b58c(hex):
    return base58.b58encode_check(hex)

def sha256(hex):
    return hashlib.sha256(hex).digest()

def find_keys(filename):
    keys = set()
    with open(filename, "rb") as f:
        # read through target file one block at a time
        while True:
            data = f.read(readlength)
            if not data:
                break

            # look in this block for keys
            pos = 0
            while True:
                # find the magic number
                pos = data.find(magic, pos)
                if pos == -1:
                    break
                key_offset = pos + magiclen
                key_data = "\x80" + data[key_offset:key_offset + 32]
                keys.add(b58c(key_data))
                pos += 1

            # are we at the end of the file?
            if len(data) == readlength:
                # make sure we didn't miss any keys at the end of the block
                f.seek(f.tell() - (32 + magiclen))
    return keys

def main():
    if len(sys.argv) != 2:
        print "./{0} <filename>".format(sys.argv[0])
        exit()

    keys = find_keys(sys.argv[1])
    for key in keys:
        print key

if __name__ == "__main__":
    main()