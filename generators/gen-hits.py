#!/usr/bin/env python3

f=open("hits.txt","a")

cnt=1000000

padding=42

for i in range(cnt):
    f.write(f"{i:#0{padding}x}\n")
