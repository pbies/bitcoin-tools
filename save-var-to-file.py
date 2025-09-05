#!/usr/bin/env python3
import pickle

# przykładowa zmienna
data = {"klucz": 123, "lista": [1, 2, 3]}

# zapis do pliku
with open("dane.pkl", "wb") as f:
	pickle.dump(data, f)

# odczyt z pliku
with open("dane.pkl", "rb") as f:
	loaded = pickle.load(f)

print("Odczytano:", loaded)

###

#!/usr/bin/env python3
import json

# przykładowa zmienna
data = {"nazwa": "Piotr", "wiek": 30, "aktywny": True}

# zapis do pliku
with open("dane.json", "w") as f:
	json.dump(data, f)

# odczyt z pliku
with open("dane.json", "r") as f:
	loaded = json.load(f)

print("Odczytano:", loaded)

###

#!/usr/bin/env python3

# zmienna
x = 42

# zapis do pliku
with open("dane.txt", "w") as f:
	f.write(str(x))

# odczyt z pliku
with open("dane.txt", "r") as f:
	loaded = int(f.read())

print("Odczytano:", loaded)
