@echo off
REM Build Script for RustChain BBC Micro Miner
REM Requires: cc65 toolchain (ca65, ld65)

echo ============================================================
echo RustChain BBC Micro Miner - Build Script
echo Bounty #407 - LEGENDARY Tier
echo ============================================================
echo.

REM Check for ca65
where ca65 >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] ca65 not found!
    echo Please install cc65 toolchain:
    echo   - Windows: https://cc65.github.io/
    echo   - Linux: sudo apt install cc65
    echo   - macOS: brew install cc65
    exit /b 1
)

echo [1/5] Assembling miner.asm...
ca65 miner.asm -o miner.o
if %errorlevel% neq 0 (
    echo [ERROR] Failed to assemble miner.asm
    exit /b 1
)
echo [OK] miner.o created

echo.
echo [2/5] Assembling entropy.asm...
ca65 entropy.asm -o entropy.o
if %errorlevel% neq 0 (
    echo [ERROR] Failed to assemble entropy.asm
    exit /b 1
)
echo [OK] entropy.o created

echo.
echo [3/5] Assembling sha256_mini.asm...
ca65 sha256_mini.asm -o sha256.o
if %errorlevel% neq 0 (
    echo [ERROR] Failed to assemble sha256_mini.asm
    exit /b 1
)
echo [OK] sha256.o created

echo.
echo [4/5] Linking...
ld65 -o MINER -t none miner.o entropy.o sha256.o
if %errorlevel% neq 0 (
    echo [ERROR] Failed to link
    exit /b 1
)
echo [OK] MINER binary created

echo.
echo [5/5] Checking file size...
for %%A in (MINER) do set SIZE=%%~zA
echo MINER size: %SIZE% bytes

if %SIZE% gtr 8192 (
    echo [WARNING] Binary exceeds 8KB target!
    echo Consider optimizing code.
) else (
    echo [OK] Size within target (8KB)
)

echo.
echo ============================================================
echo [SUCCESS] Build completed!
echo ============================================================
echo.
echo Next steps:
echo   1. Create disc image: python tools\make_ssd.py MINER LOADER.BAS -o RUSTCHN.SSD
echo   2. Test: python test_miner.py
echo   3. Deploy to BBC Micro
echo.
echo Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
echo Bounty: 200 RTC ($20) - LEGENDARY Tier
echo.

exit /b 0
