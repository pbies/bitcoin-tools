#!/usr/bin/env python3

def hex_to_b58c(h):
	return base58.b58encode_check(bytes.fromhex(h)).decode()

def int_to_b58c_wif(b):
	return base58.b58encode_check(b'\x80'+b.to_bytes(32,'big')).decode()

def int_to_bytes3(value, length = None):
	if not length and value == 0:
		result = [0]
	else:
		result = []
		for i in range(0, length or 1+int(math.log(value, 2**8))):
			result.append(value >> (i * 8) & 0xff)
		result.reverse()
	return bytearray(result)

def getWif(privkey):
	wif = b"\x80" + privkey
	wif = b58(wif + sha256(sha256(wif))[:4])
	return wif

def b58(data):
	B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
	if data[0] == 0:
		return "1" + b58(data[1:])
	x = sum([v * (256 ** i) for i, v in enumerate(data[::-1])])
	ret = ""
	while x > 0:
		ret = B58[x % 58] + ret
		x = x // 58
	return ret

def sha256(data):
	digest = hashlib.new("sha256")
	digest.update(data)
	return digest.digest()

def bytes_to_int(k):
	return int.from_bytes(k,'big')

def pvk_to_wif(key_bytes):
	return base58.b58encode_check(b'\x80' + key_bytes)

def pvk_to_wif2(key_hex):
	return base58.b58encode_check(b'\x80' + bytes.fromhex(key_hex))

def int_to_bytes4(number, length):
	return number.to_bytes(length,'big')

def find_all_matches(pattern, string):
	pat = re.compile(pattern)
	pos = 0
	out = []
	while (match := pat.search(string, pos)) is not None:
		pos = match.start() + 1
		out.append(match[0])
	return out

# pubkey compress to uncompress

import binascii

p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

def decompress_pubkey(pk):
    x = int.from_bytes(pk[1:33], byteorder='big')
    y_sq = (pow(x, 3, p) + 7) % p
    y = pow(y_sq, (p + 1) // 4, p)
    if y % 2 != pk[0] % 2:
        y = p - y
    y = y.to_bytes(32, byteorder='big')
    return b'\x04' + pk[1:33] + y

with open('add.txt') as f:
  for line in f:
    line=line.strip()
    print(binascii.hexlify(decompress_pubkey(binascii.unhexlify(line))).decode(),file=open("uncomp.txt", "a"))

# pubkey uncompress to compress

def cpub(x,y):
 prefix = '02' if y % 2 == 0 else '03'
 c = prefix+ hex(x)[2:].zfill(64)
 return c
with open('add.txt') as f:
  for line in f:
    line=line.strip()
    x = int(line[2:66], 16)
    y = int(line[66:], 16)
    pub04=cpub(x,y)

    print(pub04,file=open("comp.txt", "a"))
