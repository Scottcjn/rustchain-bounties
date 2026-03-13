@echo off
REM test_build.bat - Test build for HP 95LX Miner
REM 
REM This script tests if the miner compiles successfully.
REM Requires Open Watcom C compiler.

echo.
echo ========================================
echo HP 95LX Miner - Test Build
echo ========================================
echo.

REM Check if Open Watcom is available
if "%WATCOM%"=="" (
    echo [SKIP] WATCOM not set - Open Watcom compiler not available
    echo.
    echo To install Open Watcom:
    echo 1. Download from: https://github.com/open-watcom/open-watcom-v2
    echo 2. Install to C:\WATCOM (or your preferred location)
    echo 3. Set environment variable: set WATCOM=C:\WATCOM
    echo.
    echo Source files created:
    dir /B src\*.c
    echo.
    echo When WATCOM is installed, run: build.bat
    goto :end
)

echo [OK] WATCOM=%WATCOM%
echo.

REM Run the build
call build.bat

if errorlevel 1 (
    echo.
    echo [FAIL] Build failed!
    goto :error
)

echo.
echo [OK] Build successful!
echo.

REM Check output file
if exist "bin\miner.com" (
    echo [OK] Output file created: bin\miner.com
    dir /C bin\miner.com | find "miner.com"
) else (
    echo [WARN] Output file not found: bin\miner.com
)

echo.
echo ========================================
echo Test Complete
echo ========================================
echo.
echo Next steps:
echo 1. Transfer miner.com to HP 95LX (or emulator)
echo 2. Run: miner
echo 3. Verify hardware detection works
echo.

goto :end

:error
echo.
echo Build failed. Please check:
echo - Open Watcom installation
echo - Source file syntax
echo - Memory model settings
echo.

:end
