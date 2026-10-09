param([ValidateSet('Start','Stop')][string]$Action, [string]$Tag='production')
$ErrorActionPreference='Stop'
$out='C:\Strata\local-setup\optimization-262k'
$launcherPath='<USER_HOME>\scripts\Start-Strata-Qwen38-Flash-Next-GSQ-RCO-IQ3_S-Vision.ps1'
$configPath='C:\Strata\strata-iq3_s.json'
function Test-StrataLauncher($Process) {
    $Process.Name -in @('powershell.exe','pwsh.exe') -and
        $Process.CommandLine -match ('(?i)(?:^|\s)-File\s+"?' + [regex]::Escape($launcherPath) + '"?(?:\s|$)')
}
function Test-StrataServer($Process) {
    $Process.Name -in @('python.exe','pythonw.exe') -and
        $Process.CommandLine -match '(?i)(?:^|\s)-m\s+serve\.server(?:\s|$)' -and
        $Process.CommandLine -match ('(?i)(?:^|\s)--config\s+"?' + [regex]::Escape($configPath) + '"?(?:\s|$)')
}
function Test-StrataLive($Process) {
    # WMI can retain exited venv-launcher records. Verify actual process state.
    $live=Get-Process -Id $Process.ProcessId -ErrorAction SilentlyContinue
    $null -ne $live -and -not $live.HasExited
}
function Get-StrataProcesses {
    @(Get-CimInstance Win32_Process | Where-Object {
        ((Test-StrataLauncher $_) -or (Test-StrataServer $_) -or
        ($_.Name -match '^strata.*\.exe$' -and $_.ExecutablePath -like 'C:\Strata\*')) -and
        (Test-StrataLive $_)
    })
}
if ($Action -eq 'Stop') {
    $owner=Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($owner) {
        $target=Get-CimInstance Win32_Process -Filter "ProcessId=$($owner.OwningProcess)"
        if (-not (Test-StrataServer $target)) { throw 'Unexpected port owner' }
    }
    $owned=@(Get-StrataProcesses)
    $ownedIds=@($owned | ForEach-Object ProcessId)
    # Stop each highest validated ancestor, including launchers without listeners.
    foreach($target in $owned | Where-Object { $_.ParentProcessId -notin $ownedIds }) {
        $fresh=Get-CimInstance Win32_Process -Filter "ProcessId=$($target.ProcessId)"
        if($null -eq $fresh -or -not (Test-StrataLive $fresh)){continue}
        if($fresh.CreationDate -ne $target.CreationDate -or $fresh.CommandLine -ne $target.CommandLine){
            throw 'Process identity changed before cleanup'
        }
        & taskkill.exe /PID $fresh.ProcessId /T /F
        if($LASTEXITCODE -ne 0 -and (Test-StrataLive $fresh)){throw 'Could not stop validated launcher tree'}
    }
    for($attempt=0;$attempt -lt 50;$attempt++) {
        $remaining=@(Get-StrataProcesses)
        if($remaining.Count -eq 0){break}
        Start-Sleep -Milliseconds 100
    }
    if($remaining.Count){throw ('Live Strata processes remain: '+(($remaining | ForEach-Object ProcessId) -join ','))}
    Write-Output 'Cleanup verified: no live Strata launcher, server, engine or vision process.'
} else {
    if (@(Get-StrataProcesses).Count) { throw 'Strata launcher/server/engine already running; stop its validated tree first' }
    if (Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue) { throw 'Port 8080 occupied' }
    nvidia-smi --query-gpu=memory.used,memory.free --format=csv
    $launch=Start-Process powershell.exe -WindowStyle Hidden -WorkingDirectory C:\Strata -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',$launcherPath) -RedirectStandardOutput "$out\$Tag.stdout.log" -RedirectStandardError "$out\$Tag.stderr.log" -PassThru
    $launch.Id | Set-Content C:\Strata\local-setup\launcher.pid
    Write-Output "Launcher PID $($launch.Id)"
}
