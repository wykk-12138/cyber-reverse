param()
$ErrorActionPreference = 'Continue'

"=== elevation & counters ==="
$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
"Elevated        : $admin"
try { $v = (Get-Counter '\Processor(_Total)\% Processor Time' -ErrorAction Stop).CounterSamples.CookedValue
      "Perf counters   : OK (cpu sample $([math]::Round($v,1)))" }
catch { "Perf counters   : BROKEN ($($_.Exception.Message.Split(',')[0]))" }

""
"=== shutdown / boot hang reports (Diagnostics-Performance) ==="
$log = 'Microsoft-Windows-Diagnostics-Performance/Operational'
$ev = Get-WinEvent -LogName $log -MaxEvents 400 -ErrorAction SilentlyContinue
if (-not $ev) { "  log unavailable" }
else {
    # 100 boot performance monitoring, 101 slow boot, 102-110 shutdown/boot degradation, 200 shutdown degradation
    $ev | Where-Object { $_.Id -in 100, 101, 102, 103, 106, 109, 110, 200 } | Select-Object -First 12 | ForEach-Object {
        $m = ($_.Message -split "`n" | Where-Object { $_ -match '\S' } | Select-Object -First 3) -join ' | '
        "  {0}  Id {1,-4} {2}" -f $_.TimeCreated, $_.Id, $m.Substring(0, [Math]::Min(150, $m.Length))
    }
}

""
"=== apps/services that delayed shutdown (event 203/204 style) ==="
$ev | Where-Object { $_.Id -in 203, 204, 205, 206, 207, 209 } | Select-Object -First 10 | ForEach-Object {
    $m = (($_.Message -split "`n") | Where-Object { $_ -match '\S' } | Select-Object -First 2) -join ' | '
    "  {0}  Id {1,-4} {2}" -f $_.TimeCreated, $_.Id, $m
}

""
"=== Kernel-Power 41 detail (last 4) ==="
Get-WinEvent -FilterHashtable @{ LogName = 'System'; Id = 41 } -MaxEvents 4 -ErrorAction SilentlyContinue | ForEach-Object {
    $x = [xml]$_.ToXml()
    $data = ($x.Event.EventData.Data | ForEach-Object { "$($_.Name)=$($_.'#text')" }) -join ' '
    "  {0}`n     {1}" -f $_.TimeCreated, $data.Substring(0, [Math]::Min(220, $data.Length))
}

""
"=== third-party services that failed at this boot ==="
Get-WinEvent -FilterHashtable @{ LogName = 'System'; Id = 7000, 7009, 7031, 7034; StartTime = (Get-Date).AddHours(-2) } -ErrorAction SilentlyContinue |
    ForEach-Object { "  {0} Id {1,-5} {2}" -f $_.TimeCreated, $_.Id, (($_.Message -split "`n")[0]) } | Select-Object -First 14

""
"=== fast startup / hibernate ==="
$hib = (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power' -ErrorAction SilentlyContinue).HiberbootEnabled
"Fast startup (HiberbootEnabled) : $hib   (1 = on; it is a common cause of shutdown hangs)"
