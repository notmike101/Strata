[CmdletBinding()]
param(
    [string]$HostAddress = '0.0.0.0',
    [ValidateRange(1, 65535)]
    [int]$Port = 8080,
    [string]$ApiKey = ''
)

$ErrorActionPreference = 'Stop'

$strataRoot = 'C:\Strata'
$pythonPath = 'C:\Strata\.venv\Scripts\python.exe'
$configPath = 'C:\Strata\strata-iq3_s.json'
$modelPath = 'C:\models\Qwen3.8-Flash-Next\IQ3_S\Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf'
$mmprojPath = 'C:\models\Qwen3.8-Flash-Next\mmproj-F16.gguf'

foreach ($requiredFile in @($pythonPath, $configPath, $modelPath, $mmprojPath)) {
    if (-not (Test-Path -LiteralPath $requiredFile -PathType Leaf)) {
        throw "Required file not found: $requiredFile"
    }
}
for ($shard = 2; $shard -le 2; $shard++) {
    $shardPath = $modelPath.Replace('00001-of-00002', ('{0:D5}-of-00002' -f $shard))
    if (-not (Test-Path -LiteralPath $shardPath -PathType Leaf)) {
        throw "Required model shard not found: $shardPath"
    }
}

$config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
$contextIndex = [Array]::IndexOf([string[]]$config.args, '--max-context')
if ($contextIndex -lt 0 -or [int]$config.args[$contextIndex + 1] -lt 262144) {
    throw "Strata must be configured for at least 262144 context tokens: $configPath"
}
if ($null -eq $config.vision -or $config.vision.mmproj -ne $mmprojPath) {
    throw "Strata must use the compatible Flash-Next vision projector: $mmprojPath"
}
foreach ($requiredFile in @($config.exe, $config.vision.exe)) {
    if (-not (Test-Path -LiteralPath $requiredFile -PathType Leaf)) {
        throw "Required engine not found: $requiredFile"
    }
}

$portOwner = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -ne $portOwner) {
    throw "TCP port $Port is already in use by PID $($portOwner.OwningProcess)."
}

$serverArgs = @(
    '-m', 'serve.server',
    '--engine', 'strata',
    '--config', $configPath,
    '--host', $HostAddress,
    '--port', $Port.ToString()
)
if (-not [string]::IsNullOrWhiteSpace($ApiKey)) {
    $serverArgs += @('--api-key', $ApiKey)
}

Write-Host "Starting Strata Qwen3.8-Flash-Next GSQ-RCO IQ3_S Vision at http://${HostAddress}:$Port"
Write-Host "Model: $modelPath"
Write-Host "Context: $($config.args[$contextIndex + 1]); vision projector: $mmprojPath"
Write-Host 'Close this window or press Ctrl+C to stop the server.'

Push-Location -LiteralPath $strataRoot
$previousApiKey = $env:STRATA_API_KEY
try {
    $env:STRATA_API_KEY = $ApiKey
    & $pythonPath @serverArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Strata exited with code $LASTEXITCODE"
    }
}
finally {
    $env:STRATA_API_KEY = $previousApiKey
    Pop-Location
}
