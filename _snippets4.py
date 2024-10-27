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
