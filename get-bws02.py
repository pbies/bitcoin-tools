#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time

url = 'https://privatekeys.pw/brainwallet/bitcoin/'
outfile=open('result.txt','w')

for i in tqdm(range(1, 439)): # 1, 439
	response = requests.get(f'{url}{i}',headers={"Content-Type":"text/html","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"})
	soup = BeautifulSoup(response.text, 'html.parser')
	bws = soup.find_all('span', class_='hover')
	#print(response.status_code)
	for bw in bws:
		outfile.write(f"{bw.get_text().strip()}\n")

	outfile.flush()
	time.sleep(1)
