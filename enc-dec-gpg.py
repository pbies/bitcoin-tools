#!/usr/bin/env python3

import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import subprocess
import gpgme
import tempfile
import os
import shutil

def encrypt_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        passphrase = simpledialog.askstring("GPG Passphrase", "Enter your passphrase:")

        # Check if the encrypted file already exists
        encrypted_file_path = file_path + ".gpg"
        if os.path.exists(encrypted_file_path):
            overwrite = messagebox.askyesno("Overwrite File", f"The encrypted file '{encrypted_file_path}' already exists. Overwrite?")
            if not overwrite:
                return

        try:
            subprocess.run(["gpg", "-c", "--cipher-algo", "AES256", "--batch", "--yes", "--passphrase", passphrase, file_path], check=True)
            print("File encrypted successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error encrypting file: {e}")

def decrypt_file():
    input_file_path = filedialog.askopenfilename()
    if input_file_path:
        output_file_path = input_file_path[:-4]

        passphrase = simpledialog.askstring("GPG Passphrase", "Enter your passphrase:")

        with tempfile.NamedTemporaryFile('w', delete=False) as temp_file:
            temp_file.write(passphrase)

        if os.path.exists(output_file_path):
            overwrite = messagebox.askyesno("Overwrite File", f"The file '{output_file_path}' already exists. Overwrite?")
            if not overwrite:
                return

        try:
            subprocess.run(["gpg", "--batch", "--passphrase-file", temp_file.name, "--decrypt", "--yes", "--output", output_file_path, input_file_path], check=True)
            print("File decrypted successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error decrypting file: {e}")
        finally:
            os.remove(temp_file.name)

# Create the main window
window = tk.Tk()
window.title("GPG File Encryption/Decryption")

# Create buttons for encryption and decryption
encrypt_button = tk.Button(window, text="Encrypt File", command=encrypt_file)
encrypt_button.pack(pady=10)

decrypt_button = tk.Button(window, text="Decrypt File", command=decrypt_file)
decrypt_button.pack(pady=10)

window.mainloop()

# (C) 2024 Aftermath @Tzeeck using Gemini
