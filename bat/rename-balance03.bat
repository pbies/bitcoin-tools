@echo off
setlocal enabledelayedexpansion

set BITCOIN_CLI=C:\111\bitcoin-cli.exe
set WALLETS_DIR=D:\Bitcoin\wallets

for %%W in ("%WALLETS_DIR%\*.dat") do (
    set WALLET_NAME=%%~nW
    set WALLET_FILE=%%~nxW

    %BITCOIN_CLI% loadwallet "!WALLET_FILE!" >nul 2>&1

    for /f "usebackq delims=" %%B in (`powershell -NoProfile -Command "& { $j = & '%BITCOIN_CLI%' -rpcwallet='!WALLET_FILE!' getbalances 2>$null | ConvertFrom-Json; $j.mine.trusted }"`) do (
        set BALANCE=%%B
    )

    %BITCOIN_CLI% -rpcwallet="!WALLET_FILE!" unloadwallet >nul 2>&1

    if defined BALANCE (
        set NEWNAME=!WALLET_NAME! - !BALANCE! BTC
        ren "%%~fW" "!NEWNAME!.dat"
        echo Renamed: !WALLET_NAME! -^> !NEWNAME!
    ) else (
        echo FAILED: !WALLET_NAME!
    )

    set BALANCE=
)

echo Done.
pause
