#!/usr/bin/env python3

import os

o=open("data.bin","wb")
o.write(os.urandom(160000))
