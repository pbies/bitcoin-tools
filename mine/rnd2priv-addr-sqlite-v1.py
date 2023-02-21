#!/usr/bin/env python3

from bitcoin import *
from subprocess import check_output
from tqdm import tqdm
import base58
import hashlib
import sqlite3

conn = sqlite3.connect("bitcoin_keys.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS keys (wif TEXT, pubaddr TEXT, str TEXT)")

no=10000

for i in tqdm(range(1,no), total=no, unit=" keys"):
	x=os.urandom(32)
	sha=hashlib.sha256(x).digest()
	tmp=b'\x80'+sha
	privkey=base58.b58encode_check(tmp).decode('utf-8')
	addr=privtoaddr(privkey)
	wif=encode_privkey(privkey, 'wif')
	cursor.execute("INSERT INTO keys VALUES (?, ?, ?)", (wif.encode('utf-8'), str.encode(addr), x))
	conn.commit()

conn.close()
