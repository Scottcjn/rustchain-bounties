@echo off
REM Run HP 95LX miner in DOSBox
REM This batch file mounts the bin directory and runs miner.com

"DOSBox.exe" -c "mount c C:\Users\48973\.openclaw-autoclaw\workspace\miners\hp-95lx\bin" -c "c:" -c "miner" -c "exit"
