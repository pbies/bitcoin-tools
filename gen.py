#!/usr/bin/env python3

# sudo apt install python3-pip
# pip3 install hdwallet

from hdwallet import HDWallet
from hdwallet.symbols import BTC
import pprint
import random

hdwallet = HDWallet(symbol=BTC)
r=hex(random.randint(0,2**512))[2:]
r='0'*(128-len(r))+r
hdwallet.from_seed(seed=r)
hdwallet.from_path(path="m/44'/0'/0'/0/0")

resp="""<!DOCTYPE html>
<html lang="en">
    <head>
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<meta http-equiv="Content-type" content="text/html;charset=utf-8">
	<title>!</title>
    </head>
    <body>
	<pre>
"""

fin="""
	</pre>
    </body>
</html>
"""

pp = pprint.PrettyPrinter(depth=4)

d = hdwallet.dumps()
s = pp.pformat(d)
resp=resp+s

resp=resp+fin

def index(req):
	return(resp)

print(s)
