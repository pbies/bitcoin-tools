#!/usr/bin/env python3

import time
from web3 import Web3
from decimal import Decimal

# Konfiguracja Web3
INFURA_URL = "https://mainnet.infura.io/v3/4246036b6cac41be88a43a5955ff5866"
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

if not web3.is_connected():
	print("Nie udało się połączyć z Ethereum Mainnet.")
	exit()

print("Połączono z Ethereum Mainnet.")

# Konfiguracja adresów i ABI
UNISWAP_ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"  # Adres Uniswap V3 Router
SUSHISWAP_ROUTER_ADDRESS = "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac" # "0xd9e1CE17f2641f24aE83637ab66a2cca9C378B9F" # "0xc0aee478e3658e2610c5f7a4a2e1777ce9e4f2ac"  # Adres SushiSwap Router

# ABI routera
UNISWAP_ABI = [
    {
        "constant": True,
        "inputs": [
            {
                "name": "amountIn",
                "type": "uint256"
            },
            {
                "name": "path",
                "type": "address[]"
            }
        ],
        "name": "getAmountsOut",
        "outputs": [
            {
                "name": "",
                "type": "uint256[]"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {
                "name": "amountIn",
                "type": "uint256"
            },
            {
                "name": "amountOutMin",
                "type": "uint256"
            },
            {
                "name": "path",
                "type": "address[]"
            },
            {
                "name": "to",
                "type": "address"
            },
            {
                "name": "deadline",
                "type": "uint256"
            }
        ],
        "name": "swapExactTokensForTokens",
        "outputs": [
            {
                "name": "amounts",
                "type": "uint256[]"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]
  # Podaj tutaj ABI Uniswap Router
SUSHISWAP_ABI = [
    {
        "constant": False,
        "inputs": [
            {
                "name": "amountIn",
                "type": "uint256"
            },
            {
                "name": "amountOutMin",
                "type": "uint256"
            },
            {
                "name": "path",
                "type": "address[]"
            },
            {
                "name": "to",
                "type": "address"
            },
            {
                "name": "deadline",
                "type": "uint256"
            }
        ],
        "name": "swapExactTokensForTokens",
        "outputs": [
            {
                "name": "amounts",
                "type": "uint256[]"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {
                "name": "amountIn",
                "type": "uint256"
            },
            {
                "name": "path",
                "type": "address[]"
            }
        ],
        "name": "getAmountsOut",
        "outputs": [
            {
                "name": "",
                "type": "uint256[]"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]
  # Podaj tutaj ABI SushiSwap Router

uniswap_router = web3.eth.contract(address=UNISWAP_ROUTER_ADDRESS, abi=UNISWAP_ABI)
sushiswap_router = web3.eth.contract(address=SUSHISWAP_ROUTER_ADDRESS, abi=SUSHISWAP_ABI)

# Klucz prywatny i adres portfela (UWAGA: Nigdy nie udostępniaj swojego klucza prywatnego!)
PRIVATE_KEY = "722640a596f3fcf40415c9528a4536ac9afd8ca1af7cf33cd9391118087b6f5b"
WALLET_ADDRESS = web3.to_checksum_address("0xa4B5401190f4886312c935aBfdB04f8AD8d4EB6D")

# Funkcja sprawdzająca cenę tokenu na giełdzie
def get_price(router, token_in, token_out, amount_in):
	amount_in_wei = web3.to_wei(amount_in, 'ether')
	amounts_out = router.functions.getAmountsOut(amount_in_wei, [token_in, token_out]).call()
	amount_out_wei = amounts_out[-1]
	return web3.from_wei(amount_out_wei, 'ether')

# Funkcja arbitrażowa
def arbitrage(token_in, token_out, amount_in):
	print("Sprawdzanie możliwości arbitrażu...")

	# Pobierz ceny na obu giełdach
	price_uniswap = get_price(uniswap_router, token_in, token_out, amount_in)
	price_sushiswap = get_price(sushiswap_router, token_in, token_out, amount_in)

	print(f"Cena na Uniswap: {price_uniswap}")
	print(f"Cena na SushiSwap: {price_sushiswap}")

	# Sprawdź możliwości arbitrażu
	if price_uniswap > price_sushiswap:
		profit = price_uniswap - price_sushiswap
		print(f"Możliwość arbitrażu! Kup na SushiSwap, sprzedaj na Uniswap. Zysk: {profit}")
		# Tutaj można dodać funkcję wykonującą transakcje
	elif price_sushiswap > price_uniswap:
		profit = price_sushiswap - price_uniswap
		print(f"Możliwość arbitrażu! Kup na Uniswap, sprzedaj na SushiSwap. Zysk: {profit}")
		# Tutaj można dodać funkcję wykonującą transakcje
	else:
		print("Brak możliwości arbitrażu.")

# Adresy tokenów (np. ETH i USDC)
TOKEN_IN = web3.to_checksum_address("0xC02aaA39b223FE8D0A0E5C4F27eAD9083C756Cc2")  # WETH
TOKEN_OUT = web3.to_checksum_address("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")  # USDC

# Główna pętla bota
AMOUNT_IN = Decimal('0.1')  # Ilość tokenu wejściowego (np. 0.1 ETH)

while True:
	try:
	arbitrage(TOKEN_IN, TOKEN_OUT, AMOUNT_IN)
	except Exception as e:
		print(f"Błąd: {e}")

	time.sleep(5)  # Odczekaj 10 sekund przed kolejnym sprawdzeniem
