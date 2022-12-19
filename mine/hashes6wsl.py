#!/usr/bin/env python3
# (C) 2022 Piotr Biesiada

import hashlib

with open("list.txt","rb") as i:
	pws = i.readlines()

o = open("listhash.txt","w")

pws = [x.strip() for x in pws]
# pws = [x.decode('ascii') for x in pws]

x1="\n"
x2="\r\n"
x3="  -\n"
x4="  -\r\n"
x5=" *-\n"
x6=" *-\r\n"

y1=x1.encode('ascii')
y2=x2.encode('ascii')
y3=x3.encode('ascii')
y4=x4.encode('ascii')
y5=x5.encode('ascii')
y6=x6.encode('ascii')

for line in pws:
	l=line.decode()

	o.write(l+x1)
	o.write(l+x2)
	o.write(l+x3)
	o.write(l+x4)
	o.write(l+x5)
	o.write(l+x6)

	l=line

	m0=hashlib.md5(l).hexdigest()
	m1=hashlib.md5(l+y1).hexdigest()
	m2=hashlib.md5(l+y2).hexdigest()
	m3=hashlib.md5(l+y3).hexdigest()
	m4=hashlib.md5(l+y4).hexdigest()
	m5=hashlib.md5(l+y5).hexdigest()
	m6=hashlib.md5(l+y6).hexdigest()

	s0=hashlib.sha256(l).hexdigest()
	s1=hashlib.sha256(l+y1).hexdigest()
	s2=hashlib.sha256(l+y2).hexdigest()
	s3=hashlib.sha256(l+y3).hexdigest()
	s4=hashlib.sha256(l+y4).hexdigest()
	s5=hashlib.sha256(l+y5).hexdigest()
	s6=hashlib.sha256(l+y6).hexdigest()

	o.write(m0+x1)
	o.write(m0+x2)
	o.write(m0+x3)
	o.write(m0+x4)
	o.write(m0+x5)
	o.write(m0+x6)

	o.write(m1+x1)
	o.write(m1+x2)
	o.write(m1+x3)
	o.write(m1+x4)
	o.write(m1+x5)
	o.write(m1+x6)

	o.write(m2+x1)
	o.write(m2+x2)
	o.write(m2+x3)
	o.write(m2+x4)
	o.write(m2+x5)
	o.write(m2+x6)

	o.write(m3+x1)
	o.write(m3+x2)
	o.write(m3+x3)
	o.write(m3+x4)
	o.write(m3+x5)
	o.write(m3+x6)

	o.write(m4+x1)
	o.write(m4+x2)
	o.write(m4+x3)
	o.write(m4+x4)
	o.write(m4+x5)
	o.write(m4+x6)

	o.write(m5+x1)
	o.write(m5+x2)
	o.write(m5+x3)
	o.write(m5+x4)
	o.write(m5+x5)
	o.write(m5+x6)

	o.write(m6+x1)
	o.write(m6+x2)
	o.write(m6+x3)
	o.write(m6+x4)
	o.write(m6+x5)
	o.write(m6+x6)

	o.write(s0+x1)
	o.write(s0+x2)
	o.write(s0+x3)
	o.write(s0+x4)
	o.write(s0+x5)
	o.write(s0+x6)

	o.write(s1+x1)
	o.write(s1+x2)
	o.write(s1+x3)
	o.write(s1+x4)
	o.write(s1+x5)
	o.write(s1+x6)

	o.write(s2+x1)
	o.write(s2+x2)
	o.write(s2+x3)
	o.write(s2+x4)
	o.write(s2+x5)
	o.write(s2+x6)

	o.write(s3+x1)
	o.write(s3+x2)
	o.write(s3+x3)
	o.write(s3+x4)
	o.write(s3+x5)
	o.write(s3+x6)

	o.write(s4+x1)
	o.write(s4+x2)
	o.write(s4+x3)
	o.write(s4+x4)
	o.write(s4+x5)
	o.write(s4+x6)

	o.write(s5+x1)
	o.write(s5+x2)
	o.write(s5+x3)
	o.write(s5+x4)
	o.write(s5+x5)
	o.write(s5+x6)

	o.write(s6+x1)
	o.write(s6+x2)
	o.write(s6+x3)
	o.write(s6+x4)
	o.write(s6+x5)
	o.write(s6+x6)
