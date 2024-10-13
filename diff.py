#!/usr/bin/env python3

# (C) 2024 Aftermath @Tzeeck

a=input('You give decimal or hex? [d/h]: ')
if a=='d':
    s=input('Start dec?: ')
    e=input('End dec?: ')
    s=int(s)
    e=int(e)
elif a=='h':
    s=input('Start hex?: ')
    e=input('End hex?: ')
    if s[0:1]=='0x':
        s=s[2:]
    if e[0:1]=='0x':
        e=e[2:]
    s=int(s,16)
    e=int(e,16)

print(f'Start = dec {s} = hex {hex(s)}')
print(f'End = dec {e} = hex {hex(e)}')

print(f'The difference = dec {e-s} = hex {hex(e-s)}')
