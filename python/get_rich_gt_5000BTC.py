#!/usr/bin/env python3
"""Fetch Bitcoin addresses with balance >= 5000 BTC from BitInfoCharts rich list.

Usage:
	python3 get_rich_gt_5000BTC.py

Output:
	./rich_gt_5000BTC.txt  -- one address per line, format: <address>,<balance_BTC>

Notes:
	- This script scrapes public web pages. Use responsibly and respect site terms of service.
	- BitInfoCharts updates frequently; run this script whenever you want fresh data.
	- If BitInfoCharts changes their HTML, parsing may require adjustments.
"""

import re
import time
import sys

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://bitinfocharts.com/top-100-richest-bitcoin-addresses.html'
HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; PiotrBiesiadaBot/1.0; +https://biesiada.pro)'}

OUTFILE = 'rich_gt_5000BTC.txt'
MIN_BALANCE = 5000.0  # BTC

def parse_balance(text):
	# Accept strings like "Balance: 9,800 BTC ($...)" or "9,800 BTC"
	m = re.search(r'([0-9\.,]+)\s*BTC', text)
	if not m:
		return None
	s = m.group(1).replace(',', '')
	try:
		return float(s)
	except ValueError:
		return None

def scrape_page(url):
	resp = requests.get(url, headers=HEADERS, timeout=30)
	resp.raise_for_status()
	soup = BeautifulSoup(resp.text, 'html.parser')
	results = []
	# Each entry typically has an <a> linking to the address and nearby text containing 'Balance:'
	# Find all address links
	for a in soup.find_all('a', href=True):
		href = a['href']
		if '/bitcoin/address/' in href or re.match(r'^[13mnBC][A-Za-z0-9]{25,}$', a.text.strip()) or a.text.strip().startswith('bc1'):
			addr = a.text.strip()
			# Look around the element for balance text
			parent = a.parent
			balance_text = ''
			# Search siblings and parent text for 'Balance'
			for node in parent.find_all(text=True):
				if 'BTC' in node:
					balance_text = node.strip()
					break
			if not balance_text:
				# fallback: search whole parent
				balance_text = parent.get_text(separator=' ', strip=True)
			bal = parse_balance(balance_text)
			if bal is not None:
				results.append((addr, bal))
	return results

def main():
	page = 0
	all_addresses = {}
	while True:
		url = BASE_URL if page == 0 else BASE_URL.replace('.html', f'-{page+1}.html')
		print(f'Fetching {url}', file=sys.stderr)
		try:
			items = scrape_page(url)
		except Exception as e:
			print('Error fetching', url, e, file=sys.stderr)
			break
		if not items:
			# No items found — stop
			break
		new_found = 0
		for addr, bal in items:
			# Keep best observed balance for address
			if addr not in all_addresses or all_addresses[addr] < bal:
				all_addresses[addr] = bal
				new_found += 1
		# If page produced no new addresses, assume we're done
		if new_found == 0 and page > 0:
			break
		page += 1
		# polite delay
		time.sleep(1.0)

	# Filter by threshold and write to file, sorted by balance desc
	filtered = [(a, b) for a, b in all_addresses.items() if b >= MIN_BALANCE]
	filtered.sort(key=lambda x: x[1], reverse=True)
	with open(OUTFILE, 'w', encoding='utf-8') as f:
		for addr, bal in filtered:
			f.write(f"{addr},{bal:.8f}\\n")
	print(f'\aWrote {len(filtered)} addresses to {OUTFILE}', file=sys.stderr)

if __name__ == '__main__':
	main()
