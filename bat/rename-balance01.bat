@echo off
setlocal enabledelayedexpansion

set BITCOIN_CLI=bitcoin-cli
set WALLETS_DIR=D:\Bitcoin\wallets

for %%W in ("%WALLETS_DIR%\*.dat") do (
    set WALLET_NAME=%%~nW
    set WALLET_PATH=%%~fW

    %BITCOIN_CLI% loadwallet "%%~fW" >nul 2>&1

    for /f "usebackq delims=" %%B in (`%BITCOIN_CLI% -rpcwallet="!WALLET_NAME!" getbalance 2^>nul`) do (
        set BALANCE=%%B
    )

    %BITCOIN_CLI% unloadwallet "!WALLET_NAME!" >nul 2>&1

    if defined BALANCE (
        set NEWNAME=!WALLET_NAME! - !BALANCE! BTC
        ren "!WALLET_PATH!" "!NEWNAME!.dat"
        echo Renamed: !WALLET_NAME! -^> !NEWNAME!
    ) else (
        echo FAILED: !WALLET_NAME!
    )

    set BALANCE=
)

echo Done.
