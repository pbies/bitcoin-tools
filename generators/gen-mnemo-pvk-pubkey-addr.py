#!/usr/bin/env python3

from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes, Bip39MnemonicGenerator, Bip39Languages
import binascii

# Generowanie losowego źródła (seed)
def generate_random_seed():
	# Generowanie mnemonika (wielu słów) BIP39
	mnemonic = Bip39MnemonicGenerator(Bip39Languages.ENGLISH).FromWordsNumber(24)
	print(f"Generated Mnemonic: {mnemonic}")

	# Generowanie seeda z mnemonika
	seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
	return seed_bytes

# Generowanie kluczy z użyciem BIP44 dla Bitcoin (możesz zmienić na inne kryptowaluty)
def generate_keys(seed_bytes, num_keys):
	# Inicjalizacja BIP44 dla Bitcoin
	bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)

	keys = []

	for i in range(num_keys):
		# Generowanie klucza dla konta 0, zewnętrzne (change) 0 i indeksu i
		bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)

		# Pobieranie klucza prywatnego i publicznego
		private_key = bip44_acc_ctx.PrivateKey().ToWif()
		public_key = bip44_acc_ctx.PublicKey().RawCompressed().ToHex()
		
		keys.append({
			'index': i,
			'private_key': private_key,
			'public_key': public_key,
			'address': bip44_acc_ctx.PublicKey().ToAddress()
		})

	return keys

# Generowanie seeda
seed_bytes = generate_random_seed()

# Generowanie kluczy poniżej hierarchii (np. 10 kluczy)
keys = generate_keys(seed_bytes, 10)

# Wyświetlanie wygenerowanych kluczy
for key in keys:
	print(f"Index: {key['index']}, Private Key: {key['private_key']}, Public Key: {key['public_key']}, Address: {key['address']}")
