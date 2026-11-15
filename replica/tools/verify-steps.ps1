# verify-steps.ps1 — run one verification phase per invocation.
#
# R110: verify.ps1 -Full is a monolith, and this machine now kills long commands (the harness job
# runner exits 134 / 4294930435, and R108 saw two silent zero-byte runs). A monolith that cannot
# finish is not a judge. This script splits the same checks into seven short steps so each one can
# be run, reported and trusted on its own; verify.ps1 stays the full sweep for a healthy machine.
#
# Usage:
#   powershell -File tools\verify-steps.ps1 -List
#   powershell -File tools\verify-steps.ps1 -Step 2
#   powershell -File tools\verify-steps.ps1 -All        (runs them in order, stops at nothing)
param(
    [int]$Step = 0,
    [switch]$All,
    [switch]$List
)

$ErrorActionPreference = 'Continue'
$dotnet = 'D:\tools\dotnet8\dotnet.exe'
$proj = 'tests\Cybersole.Tests\Cybersole.Tests.csproj'

$steps = @(
    @{ N = 1; Name = 'release build';        Run = { & $dotnet build .\Cybersole.sln -c Release -v q --nologo 2>&1 | Out-String } },
    @{ N = 2; Name = 'unit tests';           Run = { & $dotnet test $proj --filter 'Speed!=Slow' -v q --nologo 2>&1 | Out-String } },
    @{ N = 3; Name = 'slow (network)';       Run = { & $dotnet test $proj --filter 'Speed=Slow&FullyQualifiedName!~Kasada' -v q --nologo 2>&1 | Out-String } },
    @{ N = 4; Name = 'slow (kasada live)';   Run = { & $dotnet test $proj --filter 'Speed=Slow&FullyQualifiedName~Kasada' -v q --nologo 2>&1 | Out-String } },
    @{ N = 5; Name = 'store modules';        Run = { & $dotnet test $proj --filter 'FullyQualifiedName~StoreModuleTests' -v q --nologo 2>&1 | Out-String } },
    @{ N = 6; Name = 'docs present';         Run = {
            $missing = @()
            foreach ($d in @('docs\PARITY.md', 'docs\WIRING.md', 'docs\VERDICT.md',
                             'docs\NIKE_PARITY.md', 'docs\IDB_EVIDENCE.md',
                             'docs\ENDPOINT_FAMILIES.md', 'docs\shopify_hosts.txt',
                             'docs\SESSION_STATE.md', 'README.md')) {
                if (-not (Test-Path $d)) { $missing += $d }
            }
            if ($missing) { "missing: " + ($missing -join ', ') } else { 'all docs present' } } },
    @{ N = 7; Name = 'mutation guards';      Run = { & 'D:\projects\IDA-pro\python311\python.exe' .\tools\mutation-check.py 2>&1 | Out-String } },
    # R128: every endpoint literal must appear verbatim in the string pool. This is the gate that
    # would have caught the Scheels /v5/Order/ invention twelve rounds before it was noticed.
    @{ N = 8; Name = 'endpoint provenance';  Run = { & 'D:\projects\IDA-pro\python311\python.exe' .\tools\endpoint-provenance.py 2>&1 | Out-String } }
)

if ($List) {
    $steps | ForEach-Object { "{0}  {1}" -f $_.N, $_.Name }
    return
}

function Invoke-Step($s) {
    $out = & $s.Run
    $code = $LASTEXITCODE

    # R113: the two live phases touch real hosts, and a single one of them loses a host in roughly
    # every other run while passing on its own (Monitor_Survives_An_Unreachable_Host / superswipe was
    # the most recent). Retry those once; the other five steps are deterministic and are not retried.
    if ($code -ne 0 -and $s.Name -like 'slow*') {
        Write-Host ("  [retry] {0} failed once — retrying" -f $s.Name)
        $out = & $s.Run
        $code = $LASTEXITCODE
        if ($code -eq 0) { Write-Host ("  [retry] {0} green on retry" -f $s.Name) }
    }

    $ok = if ($null -eq $code) { -not ($out -match 'missing:') } else { $code -eq 0 }
    if ($out -match 'error CS') { $ok = $false }

    $detail = if ($ok) { 'ok' }
              else {
                  $line = ($out -split "`r?`n" |
                           Where-Object { $_ -match '(error CS|\[FAIL\]|^\s*失败 )' } |
                           Select-Object -First 1)
                  if ($line) { $line.Trim() } else { "exit $code" }
              }
    Write-Host ("{0,-22} {1}  {2}" -f $s.Name, $(if ($ok) { 'PASS' } else { 'FAIL' }), $detail)
    return $ok
}

# R130: every browser launch leaves a cyb-chromium-* profile in %TEMP% (5 MB each, 1.8 GB after a
# few hundred runs). Sweep them before the run so the cost never accumulates.
$sweep = Join-Path $PSScriptRoot 'clean-temp.ps1'
if (Test-Path $sweep) {
    try { & powershell -NoProfile -ExecutionPolicy Bypass -File $sweep | Out-Null } catch { }
}

if ($Step -gt 0) {
    $s = $steps | Where-Object { $_.N -eq $Step }
    if (-not $s) { "no such step: $Step"; exit 2 }
    if (Invoke-Step $s) { exit 0 } else { exit 1 }
}

if ($All) {
    $failed = @()
    foreach ($s in $steps) {
        if (-not (Invoke-Step $s)) { $failed += $s.Name }
    }
    ""
    if ($failed) { "FAILED: " + ($failed -join ', '); exit 1 } else { 'ALL STEPS PASSED'; exit 0 }
}
