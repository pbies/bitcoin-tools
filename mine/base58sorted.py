#!/usr/bin/env python3

import sys
import os
import base58

filein=open('./base58sorted.txt','rb');
fileout=open('./base58output.txt','wb');

while l:=filein.readline():
	x=base58.b58decode_check(l.decode("utf-8"));
	fileout.write(x);
	fileout.write(b"\n");

filein.close();
fileout.close();
