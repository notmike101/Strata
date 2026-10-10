$ErrorActionPreference = 'Stop'
$root = 'C:\Strata'
$out = "$root\local-setup\target-80"
$nsys = 'C:\Strata\.tools\n5\ProgramFiles64Folder\NVIDIA Corporation\Nsight Systems 2026.5.1\target-windows-x64\nsys.exe'
& "$root\local-setup\optimization-262k\server.ps1" -Action Stop
for ($i=0; $i -lt 60; $i++) {
    $left = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'strata*.exe' })
    if ($left.Count -eq 0) { break }
    Start-Sleep -Seconds 1
}
if ($left.Count) { throw 'Inference still resident' }
$conf = Get-Content "$root\strata-iq3_s.json" -Raw | ConvertFrom-Json
if ($conf.env.STRATA_VERIFY_PROFILE) { throw 'GPU phase stamps alter overlap; not permitted in P025' }
if (Test-Path Env:\STRATA_VERIFY_PROFILE) { throw 'Unexpected GPU phase instrumentation' }
nvidia-smi --query-gpu=memory.used,memory.free --format=csv
$logOffset = (Get-Item "$root\strata-iq3_s.log").Length
$env:STRATA_DECODE_TIMING = '1'
$profileArgs = @('profile','--trace=cuda','--cuda-graph-trace=node','--cuda-event-trace=false','--cuda-flush-interval=1000','--sample=none','--cpuctxsw=none',
    '--session-new=strata90p025','--start-later=true','--kill=false',"--output=$out\P025-decode",
    'powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',
    '<USER_HOME>\scripts\Start-Strata-Qwen38-Flash-Next-GSQ-RCO-IQ3_S-Vision.ps1')
$prof = Start-Process -FilePath $nsys -ArgumentList $profileArgs -WindowStyle Hidden -WorkingDirectory $root -PassThru `
    -RedirectStandardOutput "$out\P025-launch.stdout.log" -RedirectStandardError "$out\P025-launch.stderr.log"
Remove-Item Env:\STRATA_DECODE_TIMING
try {
    $ready = $false
    for ($i=0; $i -lt 120; $i++) {
        try { $health=Invoke-RestMethod http://127.0.0.1:8080/health -TimeoutSec 2; if($health.loaded){$ready=$true;break} } catch {}
        if ($prof.HasExited) { throw 'Profiler launcher exited before readiness' }
        Start-Sleep -Seconds 3
    }
    if (-not $ready) { throw 'Profiling server not ready' }
    & "$root\.venv\Scripts\python.exe" "$out\profile-p025.py" --config "$root\strata-iq3_s.json" --out "$out\P025-short-profile" --runs 5 --cache-hits
    if ($LASTEXITCODE -ne 0) { throw 'Profiler benchmark failed' }
} finally {
    & $nsys shutdown --session=strata90p025 --kill=false
    & "$root\local-setup\optimization-262k\server.ps1" -Action Stop
    $agents = @(Get-CimInstance Win32_Process | Where-Object {
        $_.ExecutablePath -eq $nsys -and $_.CommandLine -like '*--start-agent --session-name strata90p025 *'
    })
    foreach ($agent in $agents) { Stop-Process -Id $agent.ProcessId }
    [pscustomobject]@{log_offset=$logOffset;profile_launcher_pid=$prof.Id;capture='Both measured new/repeat requests including prompt processing; CUDA graph nodes;1000ms flush; event tracing disabled; host decode timers; diagnostic only';authoritative=$false} | ConvertTo-Json | Set-Content "$out\P025-capture.json"
}
