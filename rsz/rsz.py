#!/usr/bin/env python3

def extended_gcd(aa, bb):
    lastremainder, remainder = abs(aa), abs(bb)
    x, lastx, y, lasty = 0, 1, 1, 0
    while remainder:
        lastremainder, (quotient, remainder) = remainder, divmod(lastremainder, remainder)
        x, lastx = lastx - quotient*x, x
        y, lasty = lasty - quotient*y, y
    return lastremainder, lastx * (-1 if aa < 0 else 1), lasty * (-1 if bb < 0 else 1)

def modinv(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise ValueError
    return x % m

R = 0x00d47ce4c025c35ec440bc81d99834a624875161a26bf56ef7fdc0f5d52f843ad1
S = 0x0044e1ff2dfd8102cf7a47c21d5c9fd5701610d04953c6836596b4fe9dd2f53e3e
Z = 0x00c0e2d0a89a348de88fda08211c70d1d7e52ccef2eb9459911bf977d587784c6e
X = 0x00c477f9f65c22cce20657faa5b2d1d8122336f851a508a1ed04e479c34985bf96
K = 0x007a1a7e52797fc8caaa435d2a4dace39158504bf204fbe19f14dbb427faee50ae

N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

#proving R = (((S * K) - Z) / X) % N
print(hex((((S * K) - Z) * modinv(X,N)) % N))

#proving S = ((Z + (X * R)) / K) % N
print(hex(((Z + (X * R)) * modinv(K,N)) % N))

#proving Z = ((S * K) - (X * R)) % N
print(hex(((S * K) - (X * R)) % N))

#proving X = (((S * K) - Z) / R) % N
print(hex((((S * K) - Z) * modinv(R,N)) % N))

#proving K = ((Z + (X * R)) / S) % N
print(hex(((Z + (X * R)) * modinv(S,N)) % N))
