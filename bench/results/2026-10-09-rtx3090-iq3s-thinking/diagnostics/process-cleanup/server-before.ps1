param([ValidateSet('Start','Stop')][string]$Action, [string]$Tag='production')
$ErrorActionPreference='Stop'
$out='C:\Strata\local-setup\optimization-262k'
if ($Action -eq 'Stop') {
    $owner=Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($owner) {
        $target=Get-CimInstance Win32_Process -Filter "ProcessId=$($owner.OwningProcess)"
        if ($target.CommandLine -notlike '*serve.server*strata-iq3_s.json*') { throw 'Unexpected port owner' }
        & taskkill.exe /PID $target.ProcessId /T /F
        if ($LASTEXITCODE -ne 0) { throw 'Could not stop server' }
    }
} else {
    if (Get-Process strata,strata-vision -ErrorAction SilentlyContinue) { throw 'Inference process already resident' }
    if (Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue) { throw 'Port 8080 occupied' }
    nvidia-smi --query-gpu=memory.used,memory.free --format=csv
    $launch=Start-Process powershell.exe -WindowStyle Hidden -WorkingDirectory C:\Strata -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File','<USER_HOME>\scripts\Start-Strata-Qwen38-Flash-Next-GSQ-RCO-IQ3_S-Vision.ps1') -RedirectStandardOutput "$out\$Tag.stdout.log" -RedirectStandardError "$out\$Tag.stderr.log" -PassThru
    $launch.Id | Set-Content C:\Strata\local-setup\launcher.pid
    Write-Output "Launcher PID $($launch.Id)"
}
