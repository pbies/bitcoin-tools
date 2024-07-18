#!/usr/bin/env python3

import requests

p=requests.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt").text
with open('http.txt','w') as f:
	f.write(p)
