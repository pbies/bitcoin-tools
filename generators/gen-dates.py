#!/usr/bin/env python3
from datetime import date, timedelta

start = date(1900, 1, 1)
end = date(2100, 1, 1)
day = timedelta(days=1)

current = start
while current <= end:
	print(current.isoformat())
	current += day
