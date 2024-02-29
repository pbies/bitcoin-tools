out = [0] * 99
out[::2], out[1::2] = range(50, 100), range(49, 0, -1)
print(out)

###

print([x for i in range(50) for x in {50-i:0,50+i:0}])

###

print([50 - i//2 * (-1)**i for i in range(1, 100)])
