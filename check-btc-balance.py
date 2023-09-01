#!/usr/bin/env python3

import json
import requests
from pprint import pprint

address_list = open('addrs.txt','r').readlines()
for addr in address_list:
	addr=addr.rstrip('\n')
	r=requests.get(f"https://blockstream.info/api/address/{addr}").text
	j=json.loads(r)
	pprint(j)
