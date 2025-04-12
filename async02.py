#!/usr/bin/env python3

# pip install aiohttp

import asyncio
import aiohttp

async def fetch(session, url):
	async with session.get(url) as response:
		print(f"Pobrano {url} - status: {response.status}")
		text = await response.text()
		return text[:100]  # Zwróć pierwsze 100 znaków

async def main():
	urls = [
		"https://www.example.com",
		"https://httpbin.org/get",
		"https://www.python.org",
	]

	async with aiohttp.ClientSession() as session:
		tasks = [fetch(session, url) for url in urls]
		results = await asyncio.gather(*tasks)

	for i, result in enumerate(results, 1):
		print(f"\nFragment zawartości {i}:")
		print(result)

asyncio.run(main())
