$ErrorActionPreference = 'Stop'
$helper = 'C:\Strata\local-setup\optimization-262k\server.ps1'
$launcher = '<USER_HOME>\scripts\Start-Strata-Qwen38-Flash-Next-GSQ-RCO-IQ3_S-Vision.ps1'
$script:processes = @()
$script:killed = @()
$script:listener = $null
function Get-NetTCPConnection { param($LocalPort,$State,$ErrorAction) $script:listener }
function Get-CimInstance {
    param($ClassName,$Filter)
    if ($Filter) { $wanted=[int]($Filter -replace 'ProcessId=',''); @($script:processes | Where-Object ProcessId -eq $wanted) }
    else { $script:processes }
}
function Get-Process {
    param($Id,$Name,$ErrorAction)
    if($Id) { $p=$script:processes | Where-Object ProcessId -eq $Id; if($p){[pscustomobject]@{Id=$Id;HasExited=$false}} }
}
function taskkill.exe {
    $at=[Array]::IndexOf($args,'/PID'); $target=[int]$args[$at+1]
    $script:killed += $target
    $ids=@($target)
    do { $before=$ids.Count; $ids += @($script:processes | Where-Object { $_.ParentProcessId -in $ids -and $_.ProcessId -notin $ids } | ForEach-Object ProcessId) } while($ids.Count -ne $before)
    $script:processes=@($script:processes | Where-Object { $_.ProcessId -notin $ids })
    $global:LASTEXITCODE=0
}
function New-ProcessRow($id,$parent,$name,$command) {
    [pscustomobject]@{ProcessId=$id;ParentProcessId=$parent;Name=$name;CommandLine=$command;CreationDate=[datetime]'2026-10-09T00:00:00Z';ExecutablePath='C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'}
}
$script:processes=@(New-ProcessRow 50001 1 'powershell.exe' ('powershell.exe -NoProfile -File '+$launcher))
. $helper -Action Stop
if($script:killed -notcontains 50001){throw 'FAIL: orphan launcher with no listener was left running'}
$script:killed=@()
$script:processes=@(
    (New-ProcessRow 50011 1 'powershell.exe' ('powershell.exe -NoProfile -File "'+$launcher+'"')),
    (New-ProcessRow 50012 50011 'python.exe' 'python.exe -m serve.server --config C:\Strata\strata-iq3_s.json'),
    (New-ProcessRow 50013 50012 'python.exe' 'python.exe -m serve.server --config C:\Strata\strata-iq3_s.json'))
$script:listener=[pscustomobject]@{OwningProcess=50013}
. $helper -Action Stop
if($script:killed.Count -ne 1 -or $script:killed[0] -ne 50011){throw 'FAIL: cleanup must stop the launcher root, not only the port-owning child'}
$script:killed=@();$script:processes=@(New-ProcessRow 50021 1 'python.exe' 'python.exe -m unrelated.server')
$script:listener=[pscustomobject]@{OwningProcess=50021}
$rejected=$false
try {. $helper -Action Stop} catch {$rejected=$true}
if(-not $rejected -or $script:killed.Count){throw 'FAIL: unrelated port owner must be refused without termination'}
Write-Output 'PASS: orphan launcher, descendant port owner, unrelated listener refusal'
