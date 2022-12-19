import sys
import getpass

from electrum.storage import WalletStorage

##########
# Set the path to your wallet file here.
#
path = "C:/Users/User/AppData/Roaming/Electrum/testnet/wallets/test_segwit_asdasd"
##########

s = WalletStorage(path)

if not s.file_exists():
    print("No wallet file at path!")
    sys.exit(0)

if not s.is_encrypted():
    print("This wallet is not encrypted!")
    sys.exit(0)

password = getpass.getpass("Enter your wallet password:", stream=None)
s.decrypt(password)
s.set_password(None)
s.write()
print("Wallet decrypted.")
