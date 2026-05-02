data=[
['WIF uncomp.:',wif1,'','',''],
['WIF comp.:',wif2,'','',''],
['pvk:',pvk,'','',''],
['p2pkh:',a,' : ',aaa,' BTC'],
['p2sh:',b,' : ',bbb,' BTC'],
['p2tr:',c,' : ',ccc,' BTC'],
['p2wpkh:',d,' : ',ddd,' BTC'],
['p2wpkh-in-p2sh:',e,' : ',eee,' BTC'],
['p2wsh:',f,' : ',fff,' BTC'],
['p2wsh-in-p2sh:',g,' : ',ggg,' BTC']
]

widths = [max(map(len, col)) for col in zip(*data)]
for row in data:
	line=" ".join((val.ljust(width) for val, width in zip(row, widths)))
	print(line)
