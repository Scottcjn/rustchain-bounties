<#
.SYNOPSIS
Wrapper patch script to ensure RustChain miner dependencies are met prior to execution.
#>

$vcRedistUrl = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
$installerPath = "$env:TEMP\vc_redist.x64.exe"
$minerPath = ".\rustchain-miner.exe"

Write-Host "[System] Checking RustChain Miner dependencies..."
$dllPath = "$env:SystemRoot\System32\vcruntime140.dll"

if (-Not (Test-Path $dllPath)) {
    Write-Host "[Fix] Missing vcruntime140.dll. Downloading and installing VC++ Redistributable..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $vcRedistUrl -OutFile $installerPath
    Start-Process -FilePath $installerPath -ArgumentList "/install /quiet /norestart" -Wait
    Write-Host "[Fix] Dependencies installed successfully." -ForegroundColor Green
} else {
    Write-Host "[System] Environment verified. All dependencies present." -ForegroundColor Green
}

Write-Host "[System] Starting RustChain Miner on fallback telemetry port 8081..."
if (Test-Path $minerPath) {
    Start-Process -FilePath $minerPath -ArgumentList "--telemetry-port 8081" -NoNewWindow
} else {
    Write-Host "[Error] rustchain-miner.exe not found in the current directory!" -ForegroundColor Red
    exit 1
}
