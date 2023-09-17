#!/usr/bin/env python3

from cryptos import *
from pprint import pprint
import cryptos
import subprocess
import sys

def sha256hex(h):
	return hashlib.sha256(hex_to_bytes(h)).hexdigest()

def ripemd160hex(h):
	t=hashlib.new('ripemd160')
	d=hex_to_bytes(h)
	t.update(d)
	return t.hexdigest()

def hex_to_bytes(hex):
	return bytes.fromhex(hex)

c = Bitcoin(testnet=False)

priv=b'\x2a\xad\xba\xa9\x9c\x7a\x63\xe1\x9a\x6a\x39\x18\xac\x40\xe7\x66\x13\xf5\xae\x96\xbc\x63\x32\xac\xdd\x20\xda\x24\x62\x12\x75\x8a'
#2aadbaa99c7a63e19a6a3918ac40e76613f5ae96bc6332acdd20da246212758a
addrmyfrom='1KkBjUXQ4rrB72PVonzwycJgZe6wXc3k6t'
addrmyto='12AgU3LHirufqAXKyxXyYtGMXkJ49C8yTN'
pubkeymy='048467749ab04de8f93cfec8aa40447efdb191445c7e65673c435330f83ec0ab60832c20c4cced5505f8ff6a07ed13928e4428f2b3932caa3df939cf111ae01ca8'
target='1fQJRQBAqZPkNJAL32K5NceGPXZuztjoC'
pubkeytarget='04c9b25b42c3f221a065d17927bb013cc5d2cec87f605e19c9bd476e73fb84b03dc3bda3733bb03d661efb160f5d57e8e7d94441fd19a62bb97d5b02bc3a11e6fcac'
#scr='00483045022100dfcfafcea73d83e1c54d444a19fb30d17317f922c19e2ff92dcda65ad09cba24022001e7a805c5672c49b222c5f2f1e67bb01f87215fb69df184e7c16f66c1f87c290347304402204a657ab8358a2edb8fd5ed8a45f846989a43655d2e8f80566b385b8f5a70dab402207362f870ce40f942437d43b6b99343419b14fb18fa69bee801d696a39b3410b8034c695221023927b5cd7facefa7b85d02f73d1e1632b3aaf8dd15d4f9f359e37e39f05611962103d2c0e82979b8aba4591fe39cffbf255b3b9c67b3d24f94de79c5013420c67b802103ec010970aae2e3d75eef0b44eaa31d7a0d13392513cd0614ff1c136b3b1020df53ae'
pubkey1=sha256hex(pubkeymy)
pubkey2=ripemd160(pubkey1)
print(pubkey2)
scr='76a914'+pubkey2+'88ac'
moje=c.unspent(addrmyfrom)
#jego=c.unspent(target)
ins = moje# + jego
#bal=0
#for i in jego:
#	bal += i['value']
#bal=bal-2000
outs = [{'address': addrmyto, 'value': 75000}]
tx = c.mktx(ins, outs)
for i in tx['ins']:
	i['script']=scr
#del tx['ins'][1]
tx['locktime']=0
tx['hash_type']=0x03
#tx['type']='pubkey'
tx = c.sign(tx, 0, priv)
pprint(tx)
t=serialize(tx)
#print(t)
#quit()
subprocess.run(["/mnt/c/Program Files/Bitcoin/daemon/bitcoin-cli.exe","sendrawtransaction",t])
