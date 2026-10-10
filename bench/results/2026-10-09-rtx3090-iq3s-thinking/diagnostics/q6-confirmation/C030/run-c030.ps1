$ErrorActionPreference = 'Stop'
$root = 'C:\Strata\local-setup\target-80'
$resultPath = Join-Path $root 'C030-confirmation'
if (Test-Path -LiteralPath $resultPath) { throw 'C030 output already exists; preserve prior measurements.' }
& C:\Strata\local-setup\optimization-262k\server.ps1 -Action Stop
& 'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.3\bin\nvcc.exe' --version
nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader
New-Item -ItemType Directory -Path $resultPath | Out-Null
$shape = Get-Content (Join-Path $root 'C028-tensor-shapes.json') -Raw | ConvertFrom-Json | Where-Object { $_.shape[0] -eq 2560 -and $_.shape[1] -eq 10240 }
$tensors = @($shape.names)
if ($tensors.Count -ne 22) { throw 'Expected all 22 actual Q6_K tensors.' }
for ($repeat = 0; $repeat -lt 3; $repeat++) {
    $ordered = @($tensors)
    if ($repeat -eq 1) { [array]::Reverse($ordered) }
    foreach ($name in $ordered) {
        $log = Join-Path $resultPath "repeat$repeat-$name.txt"
        & (Join-Path $root 'c030-dense-test.exe') $name C:\models\Qwen3.8-Flash-Next\IQ3_S\Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf C:\models\Qwen3.8-Flash-Next\IQ3_S\Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00002-of-00002.gguf *> $log
        if ($LASTEXITCODE -ne 0) { throw "C030 parity/timing failed: $name, repeat $repeat, exit $LASTEXITCODE" }
    }
    Write-Output "Completed repeat $repeat, 22 actual tensors."
}
nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader
