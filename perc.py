#!/usr/bin/env python3

# (C) 2024 Aftermath @Tzeeck

a=input('You give decimal or hex? [d/h]:')
if a=='d':
    s=input('Start dec?:')
    e=input('End dec?:')
    s=int(s)
    e=int(e)
elif a=='h':
    s=input('Start hex?:')
    e=input('End hex?:')
    if s[0:1]=='0x':
        s=s[2:]
    if e[0:1]=='0x':
        e=e[2:]
    s=int(s,16)
    e=int(e,16)

print(f'Start = dec {s} = hex {hex(s)}')
print(f'End = dec {e} = hex {hex(e)}')

sp=input('Start %?:')
ep=input('End %?:')
sp=float(sp)/100
ep=float(ep)/100

r=e-s
x=r*sp
x=x+s
y=r*ep
y=y+s
xi=int(x)
yi=int(y)

print(f'That\'s start = dec {xi} = hex {hex(xi)}')
print(f'That\'s end = dec {yi} = hex {hex(yi)}')
