#!/usr/bin/env python3

import asyncio

async def zadanie(nr):
	print(f"Start zadania {nr}")
	await asyncio.sleep(1)  # udajemy operację np. I/O
	print(f"Koniec zadania {nr}")
	return nr * nr

async def main():
	# odpalamy kilka zadań równolegle
	zadania = [asyncio.create_task(zadanie(i)) for i in range(5)]
	wyniki = await asyncio.gather(*zadania)
	print("Wyniki:", wyniki)

if __name__ == "__main__":
	asyncio.run(main())
