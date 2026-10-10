$ErrorActionPreference = 'Stop'
$root = 'C:\Strata\local-setup\target-80'
$resultPath = Join-Path $root 'C032-integrated'
if (Test-Path -LiteralPath $resultPath) { throw 'C032 output already exists; preserve prior measurements.' }
& C:\Strata\local-setup\optimization-262k\server.ps1 -Action Stop
nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader
New-Item -ItemType Directory -Path $resultPath | Out-Null
$shape = Get-Content (Join-Path $root 'C028-tensor-shapes.json') -Raw | ConvertFrom-Json | Where-Object { $_.shape[0] -eq 2560 -and $_.shape[1] -eq 10240 }
if (@($shape.names).Count -ne 22) { throw 'Expected 22 tensors.' }
foreach ($mode in @('0', '1')) {
    $env:STRATA_Q6_ONEWARP = $mode
    foreach ($name in $shape.names) {
        & (Join-Path $root 'c032-integrated-test.exe') $name C:\models\Qwen3.8-Flash-Next\IQ3_S\Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf C:\models\Qwen3.8-Flash-Next\IQ3_S\Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00002-of-00002.gguf *> (Join-Path $resultPath "mode$mode-$name.txt")
        if ($LASTEXITCODE -ne 0) { throw "C032 mismatch for $name, mode$mode, exit $LASTEXITCODE" }
    }
    Write-Output "PASS integrated mode${mode}: all 22 actual tensors."
}
Remove-Item Env:STRATA_Q6_ONEWARP
nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader
