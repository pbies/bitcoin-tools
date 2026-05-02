@echo off
chcp 65001
title %~f0
cls
echo %~f0

setlocal enabledelayedexpansion

for %%F in (*.dat) do (
    echo Repairing: %%F
    bitcoin-wallet -datadir=. -wallet=".\%%F" salvage
    if !errorlevel! neq 0 (
        echo FAILED: %%F
    ) else (
        echo OK: %%F
    )
)

echo Done.
pause
