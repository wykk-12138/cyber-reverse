param(
    [string]$Log = 'D:\projects\cyber-reverse\analysis\repair2.log'
)

$ErrorActionPreference = 'Continue'
function W([string]$m) {
    $line = "[{0:HH:mm:ss}] {1}" -f (Get-Date), $m
    Write-Host $line
    Add-Content -Path $Log -Value $line -Encoding UTF8
}
Set-Content -Path $Log -Value "" -Encoding UTF8

$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
W "Elevated: $admin"
if (-not $admin) { W "ABORT"; exit 2 }

W ""
W "=== 1. tokensave leftovers ==="
$targets = @(
    'C:\Users\wykk\scoop\apps\tokensave',
    'C:\Users\wykk\scoop\buckets\tokensave',
    'C:\Users\wykk\scoop\cache\tokensave#4.3.13#bcb7bf2.zip'
)

foreach ($t in $targets) {
    if (-not (Test-Path $t)) { W "  absent: $t"; continue }

    $item = Get-Item $t -Force
    W ("  target: $t  (attrs: " + $item.Attributes + ")")

    W "  takeown ..."
    (& takeown.exe /F $t /R /D Y 2>&1) | Where-Object { $_ -match '成功|SUCCESS|错误|ERROR' } | Select-Object -First 3 | ForEach-Object { W ("    " + $_) }

    W "  icacls grant ..."
    (& icacls.exe $t /grant "*S-1-5-32-544:(OI)(CI)F" /T /C 2>&1) | Where-Object { $_ -match '已成功|Successfully|失败|Failed' } | Select-Object -Last 2 | ForEach-Object { W ("    " + $_) }

    W "  remove ..."
    try {
        Get-ChildItem $t -Force -ErrorAction SilentlyContinue | ForEach-Object {
            if ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                W ("    unlink junction: " + $_.FullName)
                cmd /c rmdir "$($_.FullName)" 2>&1 | Out-Null
            }
        }
        Remove-Item $t -Recurse -Force -ErrorAction Stop
        W "    removed"
    }
    catch { W ("    FAILED: " + $_.Exception.Message) }
}

W "  leftovers now:"
Get-ChildItem 'C:\Users\wykk\scoop' -Recurse -Depth 3 -Filter '*tokensave*' -ErrorAction SilentlyContinue |
    ForEach-Object { W ("    " + $_.FullName) }

W ""
W "=== 2. minifilters ==="
(& fltmc.exe filters 2>&1) | ForEach-Object { W ("  " + $_) }

W ""
W "=== 3. AliPaladin state ==="
(& sc.exe qc AliPaladin 2>&1) | ForEach-Object { W ("  " + $_) }

W ""
W "=== 4. counters (PDH, locale-proof) ==="
$tp = & typeperf.exe '\Processor(_Total)\% Processor Time' -sc 1 2>&1
$tp | Where-Object { $_ -match '^\s*"' } | Select-Object -Last 1 | ForEach-Object { W ("  typeperf: " + $_) }
try {
    $c = New-Object System.Diagnostics.PerformanceCounter('Processor', '% Processor Time', '_Total')
    $null = $c.NextValue(); Start-Sleep -Milliseconds 300
    W ("  PerformanceCounter: {0:N1} %" -f $c.NextValue())
    $c.Dispose()
} catch { W ("  PerformanceCounter failed: " + $_.Exception.Message) }

W ""
W "=== 5. service load state at boot ==="
foreach ($n in 'tokensave-daemon', 'AliPaladin', 'cplspcon') {
    $q = & sc.exe query $n 2>&1
    W ("  {0}: {1}" -f $n, (($q | Where-Object { $_ -match 'STATE|FAILED' }) -join ' / '))
}

W ""
W "=== done ==="
