# test-chunks.ps1 — run the fast suite in chunks, so one slow launch cannot hide the rest.
#
# Why this exists (R181): on a machine whose Chromium launches have degraded, the whole fast suite inside ONE test
# process stalls indefinitely — while every test class on its own finishes in about a second. The failure mode is a
# hang, which reports nothing: no red, no names, just silence. Chunking turns that into N bounded runs whose worst
# case is "chunk k timed out", and the chunk's classes are printed.
#
#   powershell -File tools\test-chunks.ps1                 # chunks of 8 classes
#   powershell -File tools\test-chunks.ps1 -Size 5
#   powershell -File tools\test-chunks.ps1 -List
#
param(
    [int]$Size = 8,
    [int]$TimeoutSeconds = 240,
    [switch]$List
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$tests = Join-Path $root 'tests\Cybersole.Tests\Cybersole.Tests.csproj'
$DOTNET = 'D:\tools\dotnet8\dotnet.exe'

# every test class declared in the test project, in file order
$classes = Get-ChildItem (Join-Path $root 'tests\Cybersole.Tests') -Filter *.cs |
    Select-String -Pattern 'public\s+(?:sealed\s+)?class\s+(\w+)' |
    ForEach-Object { $_.Matches[0].Groups[1].Value } |
    Where-Object { $_ -match 'Tests$|Probe$' } |
    Sort-Object -Unique

if (-not $classes) { 'no test classes found'; exit 2 }

$chunks = @()
for ($i = 0; $i -lt $classes.Count; $i += $Size) {
    $chunks += , ($classes[$i..([Math]::Min($i + $Size - 1, $classes.Count - 1))])
}

if ($List) {
    $n = 1
    foreach ($c in $chunks) { "{0,2}  {1}" -f $n, ($c -join ', '); $n++ }
    "{0} classes in {1} chunks of up to {2}" -f $classes.Count, $chunks.Count, $Size
    exit 0
}

$failed = @()
$n = 1
foreach ($c in $chunks) {
    $filter = ($c | ForEach-Object { "FullyQualifiedName~$_" }) -join '|'
    $sw = [Diagnostics.Stopwatch]::StartNew()

    $job = Start-Job -ScriptBlock {
        param($dotnet, $proj, $filter)
        & $dotnet test $proj --filter $filter --nologo 2>&1 | Out-String
    } -ArgumentList $DOTNET, $tests, $filter

    if (-not (Wait-Job $job -Timeout $TimeoutSeconds)) {
        Stop-Job $job -ErrorAction SilentlyContinue
        Remove-Job $job -Force -ErrorAction SilentlyContinue
        "chunk {0,2}  TIMEOUT after {1}s  ({2})" -f $n, $TimeoutSeconds, ($c -join ', ')
        $failed += "chunk $n (timeout)"
        $n++
        continue
    }

    $out = Receive-Job $job
    Remove-Job $job -Force -ErrorAction SilentlyContinue
    $sw.Stop()

    $verdict = ($out -split "`n" | Where-Object { $_ -match '已通过!|失败!|Passed!|Failed!' } | Select-Object -First 1)
    if (-not $verdict) { $verdict = 'no verdict line' }

    if ($verdict -match '失败!|Failed!') {
        "chunk {0,2}  FAIL  {1:N1}s  ({2})" -f $n, $sw.Elapsed.TotalSeconds, ($c -join ', ')
        $out -split "`n" | Where-Object { $_ -match '\[FAIL\]' } | ForEach-Object { "          " + $_.Trim() }
        $failed += "chunk $n"
    }
    else {
        "chunk {0,2}  PASS  {1:N1}s  {2}" -f $n, $sw.Elapsed.TotalSeconds, ($verdict -replace '\s+', ' ').Trim()
    }
    $n++
}

if ($failed) { 'FAILED: ' + ($failed -join ', '); exit 1 } else { 'ALL CHUNKS PASSED'; exit 0 }
