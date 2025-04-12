#!/usr/bin/env python3

import asyncio

async def zadanie(nr):
	print(f"Start zadania {nr}")
	await asyncio.sleep(2)
	print(f"Koniec zadania {nr}")

async def main():
	await asyncio.gather(
		zadanie(1),
		zadanie(2),
		zadanie(3)
	)

asyncio.run(main())
