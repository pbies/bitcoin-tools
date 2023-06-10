#!/usr/bin/env python3

import hashlib

with open("list.txt","rb") as i:
	pws = i.readlines()

o = open("listhash.txt","wb")

pws = [x.strip() for x in pws]
# pws = [x.decode('ascii') for x in pws]

for line in pws:
	o.write(line+"\n")
	o.write(line+"\r\n")
	o.write(line+"  -\n")
	o.write(line+"  -\r\n")
	o.write(line+" *-\n")
	o.write(line+" *-\r\n")

	m0=hashlib.md5(line).hexdigest()
	m1=hashlib.md5(line+"\n").hexdigest()
	m2=hashlib.md5(line+"\r\n").hexdigest()
	m3=hashlib.md5(line+"  -\n").hexdigest()
	m4=hashlib.md5(line+"  -\r\n").hexdigest()
	m5=hashlib.md5(line+" *-\n").hexdigest()
	m6=hashlib.md5(line+" *-\r\n").hexdigest()

	s0=hashlib.sha256(line).hexdigest()
	s1=hashlib.sha256(line+"\n").hexdigest()
	s2=hashlib.sha256(line+"\r\n").hexdigest()
	s3=hashlib.sha256(line+"  -\n").hexdigest()
	s4=hashlib.sha256(line+"  -\r\n").hexdigest()
	s5=hashlib.sha256(line+" *-\n").hexdigest()
	s6=hashlib.sha256(line+" *-\r\n").hexdigest()

	o.write(m0+"\n")
	o.write(m0+"\r\n")
	o.write(m0+"  -\n")
	o.write(m0+"  -\r\n")
	o.write(m0+" *-\n")
	o.write(m0+" *-\r\n")

	o.write(m1+"\n")
	o.write(m1+"\r\n")
	o.write(m1+"  -\n")
	o.write(m1+"  -\r\n")
	o.write(m1+" *-\n")
	o.write(m1+" *-\r\n")

	o.write(m2+"\n")
	o.write(m2+"\r\n")
	o.write(m2+"  -\n")
	o.write(m2+"  -\r\n")
	o.write(m2+" *-\n")
	o.write(m2+" *-\r\n")

	o.write(m3+"\n")
	o.write(m3+"\r\n")
	o.write(m3+"  -\n")
	o.write(m3+"  -\r\n")
	o.write(m3+" *-\n")
	o.write(m3+" *-\r\n")

	o.write(m4+"\n")
	o.write(m4+"\r\n")
	o.write(m4+"  -\n")
	o.write(m4+"  -\r\n")
	o.write(m4+" *-\n")
	o.write(m4+" *-\r\n")

	o.write(m5+"\n")
	o.write(m5+"\r\n")
	o.write(m5+"  -\n")
	o.write(m5+"  -\r\n")
	o.write(m5+" *-\n")
	o.write(m5+" *-\r\n")

	o.write(m6+"\n")
	o.write(m6+"\r\n")
	o.write(m6+"  -\n")
	o.write(m6+"  -\r\n")
	o.write(m6+" *-\n")
	o.write(m6+" *-\r\n")

	o.write(s0+"\n")
	o.write(s0+"\r\n")
	o.write(s0+"  -\n")
	o.write(s0+"  -\r\n")
	o.write(s0+" *-\n")
	o.write(s0+" *-\r\n")

	o.write(s1+"\n")
	o.write(s1+"\r\n")
	o.write(s1+"  -\n")
	o.write(s1+"  -\r\n")
	o.write(s1+" *-\n")
	o.write(s1+" *-\r\n")

	o.write(s2+"\n")
	o.write(s2+"\r\n")
	o.write(s2+"  -\n")
	o.write(s2+"  -\r\n")
	o.write(s2+" *-\n")
	o.write(s2+" *-\r\n")

	o.write(s3+"\n")
	o.write(s3+"\r\n")
	o.write(s3+"  -\n")
	o.write(s3+"  -\r\n")
	o.write(s3+" *-\n")
	o.write(s3+" *-\r\n")

	o.write(s4+"\n")
	o.write(s4+"\r\n")
	o.write(s4+"  -\n")
	o.write(s4+"  -\r\n")
	o.write(s4+" *-\n")
	o.write(s4+" *-\r\n")

	o.write(s5+"\n")
	o.write(s5+"\r\n")
	o.write(s5+"  -\n")
	o.write(s5+"  -\r\n")
	o.write(s5+" *-\n")
	o.write(s5+" *-\r\n")

	o.write(s6+"\n")
	o.write(s6+"\r\n")
	o.write(s6+"  -\n")
	o.write(s6+"  -\r\n")
	o.write(s6+" *-\n")
	o.write(s6+" *-\r\n")
