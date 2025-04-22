#!/usr/bin/env python3

from bsddb3 import db
import sys

wallet_db2 = db.DB()
wallet_db2.open('empty-legacy-for-imports.dat', 'main', db.DB_BTREE, db.DB_CREATE)

print('\a', end='', file=sys.stderr)
