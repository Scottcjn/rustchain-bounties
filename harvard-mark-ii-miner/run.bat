@echo off
REM Harvard Mark II Miner - Windows Quick Start
REM 
REM Usage:
REM   run.bat              Run simulator with default settings
REM   run.bat test         Run quick test
REM   run.bat demo         Run full demo
REM   run.bat encode       Generate sample paper tape
REM   run.bat help         Show help

cd /d "%~dp0"

if "%1"=="" goto run
if "%1"=="run" goto run
if "%1"=="test" goto test
if "%1"=="demo" goto demo
if "%1"=="encode" goto encode
if "%1"=="help" goto help

echo Unknown command: %1
echo Run 'run.bat help' for usage information.
exit /b 1

:run
echo Running Harvard Mark II Miner Simulator...
python simulation\mark2_miner.py 2
goto done

:test
echo Running quick test...
python simulation\mark2_miner.py 1
goto done

:demo
echo Running full demo (3 epochs)...
python simulation\mark2_miner.py 3
goto done

:encode
echo Generating sample paper tape...
python simulation\paper_tape_encoder.py --miner sample_miner.pt
python simulation\paper_tape_decoder.py sample_miner.pt
goto done

:help
echo Harvard Mark II Miner - Quick Start
echo.
echo Usage: run.bat [command]
echo.
echo Commands:
echo   run       Run simulator ^(default, 2 epochs^)
echo   test      Quick test ^(1 epoch^)
echo   demo      Full demo ^(3 epochs^)
echo   encode    Generate sample paper tape
echo   decode    Decode a paper tape file
echo   help      Show this help message
echo.
echo Examples:
echo   run.bat              Run simulator
echo   run.bat test         Quick test
echo   run.bat decode output.pt
echo.
echo Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
echo Issue:  #393 - LEGENDARY Tier ^(200 RTC^)
goto done

:done
echo.
echo Done!
