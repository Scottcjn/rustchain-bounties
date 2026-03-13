@echo off
REM ZX Spectrum RustChain Miner - Build Script for Windows
REM Requires: Pasmo (http://pasmo.speccy.org/) or z88dk (https://z88dk.org/)

echo ============================================================
echo ZX Spectrum RustChain Miner - Build Script
echo ============================================================
echo.

REM Check for Pasmo
where pasmo >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [1/2] Building with Pasmo (assembly)...
    pasmo src/main.asm miner.tap
    if exist miner.tap (
        echo [OK] Build successful: miner.tap
        echo.
        echo To load in Fuse emulator:
        echo   fuse miner.tap
        echo.
        echo To load on real hardware:
        echo   1. Copy miner.tap to SD card (for ZXpand+)
        echo   2. Or use cassette interface (LOAD "")
        echo.
    ) else (
        echo [ERROR] Build failed!
        echo Check for assembly errors above.
        exit /b 1
    )
) else (
    echo [INFO] Pasmo not found in PATH
    echo.
    
    REM Check for z88dk
    where zcc >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo [1/2] Building with z88dk (C)...
        zcc +zx -vn -O3 -o miner.tap src/main.c
        if exist miner.tap (
            echo [OK] Build successful: miner.tap
        ) else (
            echo [ERROR] Build failed!
            exit /b 1
        )
    ) else (
        echo [ERROR] Neither Pasmo nor z88dk found in PATH
        echo.
        echo Please install one of:
        echo   - Pasmo: http://pasmo.speccy.org/
        echo   - z88dk: https://z88dk.org/
        echo.
        exit /b 1
    )
)

echo [2/2] Build complete!
echo.
echo Next steps:
echo   1. Test in Fuse emulator: fuse miner.tap
echo   2. Run PC bridge: python tools/pc_bridge.py
echo   3. Test on real ZX Spectrum hardware
echo.
echo ============================================================
