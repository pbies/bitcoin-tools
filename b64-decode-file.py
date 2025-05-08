#!/usr/bin/env python3

import base64
import sys

fn=sys.argv[1]

f=open(fn,'rb').read()

open(fn+'.decoded','wb').write(base64.b64decode(f))
