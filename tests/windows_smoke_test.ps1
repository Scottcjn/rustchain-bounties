param(
    [string]$MinerExe = ".\rustchain-miner.exe",
    [int]$TestDuration = 600
)

Write-Host "[AGI] Starting RustChain Windows Miner Smoke Test for $TestDuration seconds..."
if (-Not (Test-Path $MinerExe)) {
    Write-Error "Miner executable not found at $MinerExe"
    exit 1
}

$process = Start-Process -FilePath $MinerExe -ArgumentList "--log-level debug" -PassThru -RedirectStandardOutput "miner_stdout.log" -RedirectStandardError "miner_stderr.log" -NoNewWindow

Write-Host "[AGI] Miner process started with ID: $($process.Id)"
Start-Sleep -Seconds $TestDuration

if (-Not $process.HasExited) {
    Write-Host "[AGI] Test duration reached. Miner is still running. Stopping process..."
    Stop-Process -Id $process.Id -Force
    Write-Host "[AGI] Smoke test successful. Gathering logs..."
} else {
    Write-Warning "[AGI] Miner process exited prematurely. Check miner_stderr.log for panic details."
}

Get-Content .\miner_stderr.log -Tail 20
