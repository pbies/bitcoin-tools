import hashlib
import base58

def inverse(x, p):  # Calculate the modular inverse of x ( mod p )
    inv1 = 1
    inv2 = 0
    n = 1
    while p != 1 and p != 0:
        quotient = x // p
        inv1, inv2 = inv2, inv1 - inv2 * quotient
        x, p = p, x % p
        n = n + 1
    return inv2

def dblpt(pt, p):  # Calculate pt+pt = 2*pt
    if pt is None:
        return None
    (x, y) = pt
    if y == 0:
        return None
    slope = 3 * pow(x, 2, p) * pow(2 * y, p - 2, p)
    xsum = pow(slope, 2, p) - 2 * x
    ysum = slope * (x - xsum) - y
    return (xsum % p, ysum % p)

def addpt(p1, p2, p):  # Calculate p1+p2
    if p1 is None or p2 is None:
        return None
    (x1, y1) = p1
    (x2, y2) = p2
    if x1 == x2:
        return dblpt(p1, p)
        # calculate (y1-y2)/(x1-x2)  modulus p
    slope = (y1 - y2) * pow(x1 - x2, p - 2, p)
    xsum = pow(slope, 2, p) - (x1 + x2)
    ysum = slope * (x1 - xsum) - y1
    return (xsum % p, ysum % p)

def ptmul(pt, a, p):  # Calculate pt*a
    scale = pt
    acc = None
    while a:
        if a & 1:
            if acc is None:
                acc = scale
            else:
                acc = addpt(acc, scale, p)
        scale = dblpt(scale, p)
        a >>= 1
    return acc

def ptdiv(pt, a, p, n):  # Calculate pt/a
    divpt = inverse(a, n) % n
    return ptmul(pt, divpt, p)

def getuncompressedpub(compressed_key):
    """
    returns uncompressed public key
    """
    y_parity = int(compressed_key[:2]) - 2
    x = int(compressed_key[2:], 16)
    a = (pow(x, 3, p) + 7) % p
    y = pow(a, (p + 1) // 4, p)
    if y % 2 != y_parity:
        y = -y % p
    return (x, y)

def compresspub(uncompressed_key):
    """
    returns uncompressed public key
    """
    (x, y) = uncompressed_key
    y_parity = y & 1
    head = '02'
    if y_parity == 1:
        head = '03'
    compressed_key = head + '{:064x}'.format(x)
    return compressed_key

def hash160(hex_str):
    sha = hashlib.sha256()
    rip = hashlib.new('ripemd160')
    sha.update(hex_str)
    rip.update(sha.digest())
    return rip.hexdigest()  # .hexdigest() is hex ASCII

def getbtcaddr(pubkeyst):
    hex_str = bytearray.fromhex(pubkeyst)
    # Obtain key:
    key_hash = '00' + hash160(hex_str)
    # Obtain signature:
    sha = hashlib.sha256()
    sha.update(bytearray.fromhex(key_hash))
    checksum = sha.digest()
    sha = hashlib.sha256()
    sha.update(checksum)
    checksum = sha.hexdigest()[0:8]
    return (base58.b58encode(bytes(bytearray.fromhex(key_hash + checksum)))).decode('utf-8')

# secp256k1 constants
#Gx	= 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
#Gy	= 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
#p  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
#n	= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

Gx= 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy= 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

g = (Gx,Gy)



compressed_key   = '0379be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798'

divisor = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141




point = getuncompressedpub(compressed_key)
newpub = ptdiv(point, divisor, p, n)
(partGx, partGy) = ptdiv(g, divisor, p, n)

print ("C- PUB (", 0 ,")->", getbtcaddr(compressed_key))
print ("U- PUB (", 0 ,")->", getbtcaddr("04%064x%064x" % point))
with open(u"pub5.txt", 'a') as f:
    f.write('\n')
    i=1
    (pointx,pointy)=(partGx,partGy)

    while i<divisor:
        (newpubtempx,newpubtempy) = addpt(newpub,(pointx,p-pointy), p)
        f.write(compresspub((newpubtempx, newpubtempy)) + '| ' + getbtcaddr(compresspub((newpubtempx, newpubtempy))))
        f.write('\n')
        print ("C- PUB (",i,")->", compresspub((newpubtempx,newpubtempy)), getbtcaddr(compresspub((newpubtempx,newpubtempy))))
        (pointx,pointy) = addpt((pointx,pointy),(partGx,partGy), p)
        i=i+1