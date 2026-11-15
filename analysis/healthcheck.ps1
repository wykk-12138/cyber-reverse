param()
$ErrorActionPreference = 'Continue'

"=== 1. memory now ==="
& 'D:\projects\cyber-reverse\analysis\perfinfo.ps1'
""
& 'D:\projects\cyber-reverse\analysis\memlists.ps1'
""

"=== 2. boot / crash history ==="
$os = Get-CimInstance Win32_OperatingSystem
"LastBootUpTime : $($os.LastBootUpTime)"
"Uptime hours   : {0:N1}" -f ((Get-Date) - $os.LastBootUpTime).TotalHours

$since = (Get-Date).AddDays(-7)
$sys = Get-WinEvent -FilterHashtable @{ LogName = 'System'; StartTime = $since } -ErrorAction SilentlyContinue
"System events (7d): $($sys.Count)"

"-- power / unclean shutdown --"
$sys | Where-Object { $_.Id -in 41, 42, 109, 6005, 6006, 6008 } |
    Group-Object Id | Sort-Object Count -Descending |
    ForEach-Object { "  Id {0,-6} x{1,-4} {2}" -f $_.Name, $_.Count, $_.Group[0].ProviderName }

"-- bugcheck --"
$bc = $sys | Where-Object { $_.Id -eq 1001 -and $_.ProviderName -match 'BugCheck' }
if ($bc) {
    $bc | Select-Object -First 6 | ForEach-Object { "  {0}  {1}" -f $_.TimeCreated, (($_.Message -split "`n")[0]) }
} else { "  none" }

"-- disk / filesystem errors --"
$disk = $sys | Where-Object { $_.ProviderName -match 'disk|Ntfs|volmgr|storahci|stornvme' -and $_.Level -le 2 }
if ($disk) {
    $disk | Group-Object ProviderName, Id | Sort-Object Count -Descending | Select-Object -First 8 |
        ForEach-Object { "  {0} Id {1} x{2}" -f $_.Group[0].ProviderName, $_.Group[0].Id, $_.Count }
} else { "  none" }

"-- service failures --"
$svc = $sys | Where-Object { $_.Id -in 7000, 7009, 7011, 7023, 7024, 7031, 7034 }
if ($svc) {
    $svc | Group-Object Id | Sort-Object Count -Descending | Select-Object -First 6 |
        ForEach-Object { "  Id {0} x{1}" -f $_.Name, $_.Count }
    $svc | Select-Object -First 5 | ForEach-Object { "    {0}  {1}" -f $_.TimeCreated, (($_.Message -split "`n")[0]) }
} else { "  none" }

"-- error/critical by provider --"
$sys | Where-Object { $_.Level -le 2 } | Group-Object ProviderName | Sort-Object Count -Descending |
    Select-Object -First 8 | ForEach-Object { "  {0,-42} x{1}" -f $_.Name, $_.Count }

""
"=== 3. volumes / filesystem ==="
$dirty = fsutil dirty query C: 2>&1
"  C: $dirty"
Get-Volume | Where-Object { $_.DriveLetter } |
    Select-Object DriveLetter, FileSystemType, HealthStatus, @{n = 'SizeGB'; e = { [int]($_.Size / 1GB) } }, @{n = 'FreeGB'; e = { [int]($_.SizeRemaining / 1GB) } } |
    Format-Table -AutoSize | Out-String -Width 70

Get-CimInstance Win32_PageFileUsage |
    Select-Object Name, @{n = 'AllocGB'; e = { [math]::Round($_.AllocatedBaseSize / 1024, 1) } }, @{n = 'UsedGB'; e = { [math]::Round($_.CurrentUsage / 1024, 2) } }, @{n = 'PeakGB'; e = { [math]::Round($_.PeakUsage / 1024, 2) } } |
    Format-Table -AutoSize | Out-String -Width 70
