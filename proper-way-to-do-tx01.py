#!/usr/bin/env python3

from cryptos import *
from pprint import pprint
import cryptos
import subprocess
import sys

c = Bitcoin(testnet=False)

priv=b'\x2a\xad\xba\xa9\x9c\x7a\x63\xe1\x9a\x6a\x39\x18\xac\x40\xe7\x66\x13\xf5\xae\x96\xbc\x63\x32\xac\xdd\x20\xda\x24\x62\x12\x75\x8a'
addrmyfrom='1KkBjUXQ4rrB72PVonzwycJgZe6wXc3k6t'
addrmyto='12AgU3LHirufqAXKyxXyYtGMXkJ49C8yTN'
pubkeymy='048467749ab04de8f93cfec8aa40447efdb191445c7e65673c435330f83ec0ab60832c20c4cced5505f8ff6a07ed13928e4428f2b3932caa3df939cf111ae01ca8'
moje=c.unspent(addrmyfrom)
ins = moje
bal=78000
outs = [{'address': addrmyto, 'value': bal}]
tx = c.mktx(ins, outs)
tx['locktime']=0
tx = c.sign(tx, 0, priv)
pprint(tx)
t=serialize(tx)
subprocess.run(["/mnt/c/Program Files/Bitcoin/daemon/bitcoin-cli.exe","sendrawtransaction",t])
