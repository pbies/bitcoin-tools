#!/usr/bin/env python3

import sys
import zlib

fn=sys.argv[1]

f=open(fn,'rb').read()

open(fn+'.decoded','wb').write(zlib.decompress(f))
