param(
    [string]$Log = 'D:\projects\cyber-reverse\analysis\repair.log'
)

$ErrorActionPreference = 'Continue'
function W([string]$m) {
    $line = "[{0:HH:mm:ss}] {1}" -f (Get-Date), $m
    Write-Host $line
    Add-Content -Path $Log -Value $line -Encoding UTF8
}

Set-Content -Path $Log -Value "" -Encoding UTF8
W "=== repair run, admin check ==="
$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
W "Elevated: $admin"
if (-not $admin) { W "ABORT: not elevated"; exit 2 }

# ---------------------------------------------------------------- 1. tokensave
W ""
W "=== 1. remove tokensave ==="

W "-- existing scheduled tasks mentioning tokensave --"
Get-ScheduledTask -ErrorAction SilentlyContinue |
    Where-Object { $_.TaskName -match 'tokensave' -or ($_.Actions | ForEach-Object { $_.Execute }) -match 'tokensave' } |
    ForEach-Object { W ("  task: " + $_.TaskPath + $_.TaskName) }

W "-- run keys mentioning tokensave --"
foreach ($key in 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run',
                 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run') {
    $props = Get-ItemProperty $key -ErrorAction SilentlyContinue
    if ($props) {
        $props.PSObject.Properties |
            Where-Object { $_.Value -is [string] -and $_.Value -match 'tokensave' } |
            ForEach-Object { W ("  run: $key -> " + $_.Name + " = " + $_.Value) }
    }
}

W "-- sc query --"
$q = & sc.exe query tokensave-daemon 2>&1
$q | ForEach-Object { W ("  " + $_) }

if ($q -match 'SERVICE_NAME') {
    W "-- stop --"
    (& sc.exe stop tokensave-daemon 2>&1) | ForEach-Object { W ("  " + $_) }
    Start-Sleep -Seconds 3
    W "-- delete --"
    (& sc.exe delete tokensave-daemon 2>&1) | ForEach-Object { W ("  " + $_) }
    Start-Sleep -Seconds 2
    W "-- verify --"
    (& sc.exe query tokensave-daemon 2>&1) | ForEach-Object { W ("  " + $_) }
}

W "-- kill any running tokensave process --"
Get-Process -Name tokensave -ErrorAction SilentlyContinue | ForEach-Object {
    W ("  stopping pid " + $_.Id)
    try { $_.Kill() } catch { W ("  kill failed: " + $_.Exception.Message) }
}
Start-Sleep -Seconds 2

W "-- remove scheduled tasks --"
Get-ScheduledTask -ErrorAction SilentlyContinue |
    Where-Object { $_.TaskName -match 'tokensave' } |
    ForEach-Object {
        W ("  unregister: " + $_.TaskPath + $_.TaskName)
        try { Unregister-ScheduledTask -TaskName $_.TaskName -TaskPath $_.TaskPath -Confirm:$false -ErrorAction Stop }
        catch { W ("  failed: " + $_.Exception.Message) }
    }

W "-- scoop app folder --"
foreach ($p in @("$env:USERPROFILE\scoop\apps\tokensave",
                 "$env:USERPROFILE\scoop\persist\tokensave")) {
    if (Test-Path $p) {
        $size = [int]((Get-ChildItem $p -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1KB)
        W ("  removing $p ($size KB)")
        try { Remove-Item $p -Recurse -Force -ErrorAction Stop; W "    done" }
        catch { W ("    FAILED: " + $_.Exception.Message) }
    } else { W ("  absent: $p") }
}

W "-- scoop shims --"
Get-ChildItem "$env:USERPROFILE\scoop\shims" -Filter 'tokensave*' -ErrorAction SilentlyContinue | ForEach-Object {
    W ("  removing " + $_.FullName)
    try { Remove-Item $_.FullName -Force -ErrorAction Stop } catch { W ("    FAILED: " + $_.Exception.Message) }
}

W "-- leftover references in scoop config --"
$scoopCfg = "$env:USERPROFILE\scoop\apps\scoop\current\..\..\..\scoop.json"
Get-ChildItem "$env:USERPROFILE\scoop" -Filter 'tokensave*' -ErrorAction SilentlyContinue |
    ForEach-Object { W ("  leftover: " + $_.FullName) }

# ---------------------------------------------------------------- 2. AliPaladin
W ""
W "=== 2. AliPaladin -> manual start ==="
$q2 = & sc.exe qc AliPaladin 2>&1
$q2 | ForEach-Object { W ("  " + $_) }
(& sc.exe config AliPaladin start= demand 2>&1) | ForEach-Object { W ("  " + $_) }

# ---------------------------------------------------------------- 3. perf counters
W ""
W "=== 3. rebuild performance counters ==="
W "-- before --"
try { (Get-Counter '\Processor(_Total)\% Processor Time' -ErrorAction Stop).CounterSamples.CookedValue | ForEach-Object { W ("  cpu ok: " + $_) } }
catch { W ("  BROKEN: " + $_.Exception.Message.Split(',')[0]) }

W "-- backup WMI repository size --"
$repo = "$env:SystemRoot\System32\wbem\Repository"
if (Test-Path $repo) {
    Get-ChildItem $repo -File -ErrorAction SilentlyContinue |
        ForEach-Object { W ("  " + $_.Name + " " + [int]($_.Length / 1MB) + " MB") }
}

W "-- lodctr /R --"
(& lodctr.exe /R 2>&1) | ForEach-Object { W ("  " + $_) }

W "-- winmgmt /resyncperf --"
(& winmgmt.exe /resyncperf 2>&1) | ForEach-Object { W ("  " + $_) }
Start-Sleep -Seconds 5

W "-- after --"
try { (Get-Counter '\Processor(_Total)\% Processor Time' -ErrorAction Stop).CounterSamples.CookedValue | ForEach-Object { W ("  cpu ok: " + $_) } }
catch { W ("  STILL BROKEN: " + $_.Exception.Message.Split(',')[0]) }

# ---------------------------------------------------------------- 4. integrity
W ""
W "=== 4. integrity (read-only) ==="
W "-- DISM CheckHealth --"
$d0 = Get-Date
(& dism.exe /Online /Cleanup-Image /CheckHealth 2>&1) | Where-Object { $_ -match '\S' } | ForEach-Object { W ("  " + $_) }
W ("  took " + [int]((Get-Date) - $d0).TotalSeconds + " s")

W "-- chkdsk C: /scan --"
$c0 = Get-Date
(& chkdsk.exe C: /scan 2>&1) | Where-Object { $_ -match 'stage|错误|error|Windows has scanned|百分比|percent|KB' } | Select-Object -Last 12 | ForEach-Object { W ("  " + $_) }
W ("  took " + [int]((Get-Date) - $c0).TotalSeconds + " s")

W "-- sfc /verifyonly (this is the slow one) --"
$s0 = Get-Date
(& sfc.exe /verifyonly 2>&1) | Where-Object { $_ -match '\S' } | ForEach-Object { W ("  " + $_) }
W ("  took " + [int]((Get-Date) - $s0).TotalSeconds + " s")

W ""
W "=== done ==="
