def bytes_to_hex(bytes):
	return bytes.hex()

def bytes_to_int(bytes):
	result = 0
	for b in bytes:
		result = result * 256 + ordsix(b)
	return result

def bytes_to_str(bytes):
	return bytes.decode("utf-8")

def hex_to_bytes(hex):
	return bytes.fromhex(hex)

def hex_to_int(hex):
	return int(hex,16)

def int_to_bytes(value, length = None):
	if not length and value == 0:
		result = [0]
	else:
		result = []
		for i in range(0, length or 1+int(math.log(value, 2**8))):
			result.append(value >> (i * 8) & 0xff)
		result.reverse()
	return str(bytearray(result))

def int_to_bytes(number):
	# 32 = number of zeros preceding
	return number.to_bytes(32,'big')

def int_to_bytes(number):
	return str.encode(str(number))

def int_to_str(number):
	return str(number)

def str_to_bytes(text):
	return str.encode(text)

def str_to_hex(text):
	return "".join(x.encode('hex') for x in text)
