@echo off
REM build.bat - Build script for HP 95LX Miner
REM 
REM Requires: Open Watcom C Compiler (v2.0+)
REM Download: https://github.com/open-watcom/open-watcom-v2
REM
REM Bounty: #417 - 100 RTC
REM Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b

echo.
echo ========================================
echo RustChain HP 95LX Miner - Build Script
echo ========================================
echo.

REM Check if WATCOM is set
if "%WATCOM%"=="" (
    echo ERROR: WATCOM environment variable not set!
    echo Please set WATCOM to your Open Watcom installation path.
    echo Example: set WATCOM=C:\WATCOM
    echo.
    goto :error
)

echo WATCOM: %WATCOM%
echo.

REM Set environment variables for Open Watcom
set PATH=%WATCOM%\binnt64;%WATCOM%\binw;%PATH%
set INCLUDE=%WATCOM%\h
set LIB=%WATCOM%\lib286;%WATCOM%\lib286\dos

REM Check if compiler exists
if not exist "%WATCOM%\binw\wcl.exe" (
    echo ERROR: wcl.exe not found in %WATCOM%\binw
    echo.
    goto :error
)

echo Source files:
echo   src\main.c
echo   src\hw_95lx.c
echo   src\display.c
echo   src\serial.c
echo   src\miner.c
echo   src\keyboard.c
echo.

REM Create output directory
if not exist "bin" mkdir bin

echo Building miner.com...
echo.

REM Build command
REM -bt=dos  : Target DOS
REM -mt      : Tiny memory model (< 64 KB)
REM -ox      : Maximum optimization
REM -zq      : Quiet mode
REM -fe=     : Output filename

wcl -bt=dos -mt -ox -zq -fe=bin\miner.com src\main.c src\hw_95lx.c src\display.c src\serial.c src\miner.c src\keyboard.c

if errorlevel 1 (
    echo.
    echo BUILD FAILED!
    echo.
    goto :error
)

echo.
echo ========================================
echo BUILD SUCCESSFUL!
echo ========================================
echo.
echo Output: bin\miner.com
echo Size: 
dir /C bin\miner.com | find "miner.com"
echo.
echo To run on HP 95LX:
echo   1. Transfer miner.com to HP 95LX
echo   2. Run: miner
echo.
echo Options:
echo   miner -s         Enable serial networking
echo   miner -b 19200   Set baud rate to 19200
echo.

goto :end

:error
echo.
echo Build failed. Check error messages above.
echo.
echo Common issues:
echo   - WATCOM not set correctly
echo   - Open Watcom not installed
echo   - Source files missing
echo.
exit /B 1

:end
