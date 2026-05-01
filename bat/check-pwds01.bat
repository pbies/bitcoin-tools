@echo off
setlocal enabledelayedexpansion

set BITCOIN_CLI="D:\Bitcoin Core\bin\bitcoin-cli.exe"
set WALLETS_DIR=D:\Bitcoin\wallets
set PASSWORDS_FILE=D:\1\passwords.txt
set RESULTS_FILE=D:\1\results.txt

if not exist "%PASSWORDS_FILE%" (
    echo passwords.txt not found
    exit /b 1
)

> "%RESULTS_FILE%" echo Wallet Password Recovery Results

for %%W in ("%WALLETS_DIR%\*.dat") do (
    set WALLET_NAME=%%~nW
    set FOUND=0

    echo Testing wallet: !WALLET_NAME!

    %BITCOIN_CLI% loadwallet "%%W" >nul 2>&1

    for /f "usebackq delims=" %%P in ("%PASSWORDS_FILE%") do (
        if !FOUND!==0 (
            %BITCOIN_CLI% -rpcwallet="!WALLET_NAME!" walletpassphrase "%%P" 5 >nul 2>&1
            if !errorlevel!==0 (
                echo FOUND - Wallet: !WALLET_NAME! Password: %%P
                >> "%RESULTS_FILE%" echo FOUND - Wallet: !WALLET_NAME! Password: %%P
                %BITCOIN_CLI% -rpcwallet="!WALLET_NAME!" walletlock >nul 2>&1
                set FOUND=1
            )
        )
    )

    if !FOUND!==0 (
        echo NOT FOUND - Wallet: !WALLET_NAME!
        >> "%RESULTS_FILE%" echo NOT FOUND - Wallet: !WALLET_NAME!
    )

    %BITCOIN_CLI% unloadwallet "!WALLET_NAME!" >nul 2>&1
)

echo Done. Results in %RESULTS_FILE%
pause
