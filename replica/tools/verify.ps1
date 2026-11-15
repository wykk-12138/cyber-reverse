# One-shot verification for the Cybersole replica.
#
#   pwsh -File tools\verify.ps1              build + offline tests + docs        (~10 s)
#   pwsh -File tools\verify.ps1 -Live         also the live contracts            (~25 s)
#   pwsh -File tools\verify.ps1 -Full         also every Speed=Slow test         (~3 min)
#   pwsh -File tools\verify.ps1 -SkipLive     skip the TLS probe
#
# Why -Full exists: 250 of the 543 tests carry Trait("Speed","Slow"), and the default
# "Speed!=Slow" filter has never run them. Round 93 ran them by hand and found two that had been
# failing since the day they were written — nike-gs missing from a gate whitelist, and the
# Shopify host list four registrations out of date. Neither could be seen without this switch.
#
# -Full subsumes -Live: it runs the live contracts too, plus the Shopify host sweep, the module
# robustness matrix and the reachability scan. Run it after touching Registry.cs or any platform
# decision.
param(
    [switch]$SkipLive,
    [switch]$Live,
    [switch]$Full
)

# $ErrorActionPreference = 'Continue' means a failed method call only prints and execution
# carries on — so a detail expression that throws still yields "all checks passed". That is
# how "[SwitchParameter] does not contain a method named 'Trim'" survived a full run. Every
# detail below therefore interpolates first: "$x".Trim() is total, $x.Trim() is not.
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$dotnet = 'D:\tools\dotnet8\dotnet.exe'
if (-not (Test-Path $dotnet)) { $dotnet = 'dotnet' }

$results = @()

# An empty detail is a defect in the caller, not a property of the check.
#
# R171: a detail expression threw ("[SwitchParameter] does not contain a method named 'Trim'")
# and $ErrorActionPreference='Continue' turned that into a $null detail — so the check reported
# PASS with a blank explanation, and the conclusion was "all checks passed". The detail channel
# is now total (every call interpolates first), and this makes the remaining case visible instead
# of silent: a check whose reason cannot be stated is a check whose result cannot be trusted, so
# it becomes a FAIL naming itself. That is deliberately harsher than the throw it replaces.
function Check($name, $ok, $detail) {
    $text = "$detail".Trim()
    if (-not $text) {
        $script:results += [pscustomobject]@{
            Check  = $name
            Result = 'FAIL'
            Detail = 'detail expression produced nothing — the check cannot be read'
        }
        return
    }
    $script:results += [pscustomobject]@{
        Check  = $name
        Result = if ($ok) { 'PASS' } else { 'FAIL' }
        Detail = $text
    }
}
# A WARN is a check this script cannot evaluate reliably. It must not turn the run red — that
# would train the reader to ignore failures — but it must not disappear either.
#
# A WARN with no detail is different from a WARN with a reason: the first is indistinguishable
# from a formatting bug. So an empty detail is named rather than dropped.
function Warn($name, $detail) {
    $text = "$detail".Trim()
    if (-not $text) { $text = 'WARN without a reason — the caller forgot to say why' }
    $script:results += [pscustomobject]@{ Check = $name; Result = 'WARN'; Detail = $text }
}

# A FAIL must say what failed, and this has now gone wrong three different ways:
#
#   R171  a detail expression threw, and the verdict still printed PASS
#   R223  the detail came back empty, so the line read "failed:" and nothing else
#   R229  the detail was non-empty and useless — "exit 1" names no test at all
#
# The empty guard in Check() covers the second. This covers the third: turn raw dotnet output
# into the failure lines themselves, and return $null when there are none so the caller has to
# say something rather than print a number that looks like information.
function FailLines($output, $max = 3) {
    $lines = @($output -split "`r?`n" |
               Where-Object { $_ -match '^\s*(失败|Failed|\[xUnit\.net.*FAIL)' } |
               Select-Object -First $max)
    if ($lines.Count -eq 0) { return $null }
    return ($lines -join ' | ')
}

# ---- 1. build ----
$build = & $dotnet build Cybersole.sln -c Release -v q --nologo 2>&1 | Out-String
Check 'release build' ($build -notmatch 'error CS') ("$build".Trim().Split("`n")[-1].Trim())

# ---- 2. tests ----
# exit code is the reliable signal (console text is localised)
$test = & $dotnet test tests\Cybersole.Tests\Cybersole.Tests.csproj --filter "Speed!=Slow" -v q --nologo 2>&1 | Out-String
$testOk = ($LASTEXITCODE -eq 0)
$count = [regex]::Matches($test, '(\d+)') | ForEach-Object { $_.Groups[1].Value } | Select-Object -Last 1
# "exit 1" is not a reason. It was the whole detail for as long as this check existed, and it
# passed the empty guard because it is not empty — it is just uninformative. A reader seeing
# "unit tests FAIL exit 1" has to go run dotnet test themselves to learn anything.
$testFails = FailLines $test
$testDetail = if ($testOk) { 'exit 0' }
              elseif ($testFails) { "failed: $testFails" }
              else { "exit $LASTEXITCODE, but no failure line in the output — run dotnet test directly" }
Check 'unit tests' $testOk $testDetail

# ---- 2a. every Speed=Slow test (opt-in) ----
# These are the ones that touch real hosts: the Shopify host sweep, the module robustness
# matrix, the reachability scan, the performance probes. They cost ~3 minutes and depend on the
# network, which is why they are not in the default run — but nothing else can notice a store
# changing platform underneath a registration.
if ($Full) {
    # R108: these tests hit real hosts, and a single one of them fails in roughly every other full
    # run while passing on its own (six different tests over four rounds, each green standalone).
    # That made the terminal judgement depend on which host hiccuped, so the phase now retries the
    # whole filtered set once. A genuine regression fails both times; a hiccup fails once.
    $slow = & $dotnet test tests\Cybersole.Tests\Cybersole.Tests.csproj `
        --filter "Speed=Slow&FullyQualifiedName!~Kasada" -v q --nologo 2>&1 | Out-String
    # R63: read the exit code once, immediately. This check failed in the suite twice and passed
    # alone every time — and with only "no failure line in the output" to go on, a network hiccup
    # and a killed process were indistinguishable. Keeping the code and the tail makes the next
    # occurrence diagnosable instead of mysterious.
    $slowExit = $LASTEXITCODE
    $slowRetried = $false

    # R108: these tests hit real hosts and about half of the full runs lose one of them, while the
    # failed test passes on its own. Retrying the whole filtered set once keeps the terminal verdict
    # meaningful without turning a host hiccup into a build failure. A genuine regression fails both
    # passes; a hiccup fails one. The detail line records that the retry is what went green.
    if ($slowExit -ne 0) {
        $firstFail = ($slow -split "`r?`n" |
                      Where-Object { $_ -match '^\s*(失败|Failed|\[xUnit\.net.*FAIL)' } |
                      Select-Object -First 1)
        Write-Host ("  [retry] slow tests failed once ({0}) — retrying the set" -f "$firstFail".Trim())

        $slow = & $dotnet test tests\Cybersole.Tests\Cybersole.Tests.csproj `
            --filter "Speed=Slow&FullyQualifiedName!~Kasada" -v q --nologo 2>&1 | Out-String
        $slowExit = $LASTEXITCODE
        $slowRetried = $true
    }

    $slowOk = ($slowExit -eq 0)

    # R223: this used to extract '失败\s+(\w+)', which matches "Cybersole" out of
    # "失败 Cybersole.Tests.SomeTests.SomeMethod" and therefore reported nothing useful. When it
    # matched nothing at all the detail was the literal "failed: " — a FAIL line with no reason,
    # which is the same complaint the PASS side had in R171.
    #
    # Keep whole failure lines instead of one word: the line carries the class, the method and
    # the duration, and it is what a reader needs to find the test.
    $failLines = ($slow -split "`r?`n" |
                  Where-Object { $_ -match '^\s*(失败|Failed|\[xUnit\.net.*FAIL)' } |
                  Select-Object -First 3) -join ' | '

    $slowDetail = if ($slowOk -and $slowRetried) { 'green on retry (first pass lost a live host)' }
                  elseif ($slowOk) { 'all live/network tests green' }
                  elseif ($failLines) { 'failed: ' + $failLines }
                  else {
                      # R64: a non-zero exit with no failing test line is almost always a build or
                      # host problem, not a test result. Show the lines that say so instead of the
                      # unhelpful "no failure line".
                      $why = ($slow -split "`r?`n" |
                              Where-Object { $_ -match 'error|错误|MSB|host|crash|锁定|being used' } |
                              Select-Object -First 3) -join ' | '
                      if (-not $why) { $why = ($slow -split "`r?`n" |
                                               Where-Object { $_.Trim() } |
                                               Select-Object -Last 3) -join ' | ' }
                      "failed: exit $slowExit — $why"
                  }

    Check 'slow tests (Speed=Slow)' $slowOk $slowDetail

    # ---- 2a-bis. the Kasada live group, on its own ----
    # It downloads and evaluates a real Kasada script, so it is an order of magnitude slower than
    # the rest of the live phase. As its own check, a hang or a host hiccup here is attributable to
    # this group instead of erasing every other live result behind it.
    $kasada = & $dotnet test tests\Cybersole.Tests\Cybersole.Tests.csproj `
        --filter "Speed=Slow&FullyQualifiedName~Kasada" -v q --nologo 2>&1 | Out-String
    $kasadaExit = $LASTEXITCODE
    $kasadaOk = ($kasadaExit -eq 0)
    $kasadaFails = ($kasada -split "`r?`n" |
                    Where-Object { $_ -match '^\s*(失败|Failed|\[xUnit\.net.*FAIL)' } |
                    Select-Object -First 2) -join ' | '
    $kasadaDetail = if ($kasadaOk) { 'kasada live group green' }
                    elseif ($kasadaFails) { 'failed: ' + $kasadaFails }
                    else { "failed: exit $kasadaExit with no failing test line" }
    Check 'slow tests (kasada live)' $kasadaOk $kasadaDetail
}

# ---- 2b. live contracts (opt-in) ----
# These assert that the platform decisions still hold: that footpatrol still answers a Shopify
# cart, that funko's site id still resolves, that bstn still speaks /api/beast/. Between rounds
# 47 and 72 eight modules were found registered against the wrong platform, and not one of those
# would have shown up in an offline test — the fixtures were written from the same wrong belief
# the code was.
if ($Live) {
    $liveTests = & $dotnet test tests\Cybersole.Tests\Cybersole.Tests.csproj `
        --filter "FullyQualifiedName~LiveContractTests" -v q --nologo 2>&1 | Out-String
    $liveOk = ($LASTEXITCODE -eq 0)

    # same shape as slow tests above: the old '失败\s+(\w+)' captured the namespace, not the test
    $liveFails = FailLines $liveTests
    $liveDetail = if ($liveOk) { 'all platform decisions still hold' }
                  elseif ($liveFails) { "drifted: $liveFails" }
                  else { "exit $LASTEXITCODE, but no failure line in the output — run dotnet test directly" }

    Check 'live contracts' $liveOk $liveDetail
}

# ---- 3. module count ----
# Count only what CreateAll() actually returns. Counting every `new XModule(` in the file
# overshoots by one: RegisterShopifyHost() constructs a FlowStoreModule inside a helper, so the
# literal count was 62 while the catalogue held 61.
$registry = Get-Content 'src\Cybersole.Stores\Modules\Registry.cs' -Raw
$start = $registry.IndexOf('public static IReadOnlyList<IStoreModule> CreateAll()')
$end   = $registry.IndexOf('};', $start)
$modules = ([regex]::Matches($registry.Substring($start, $end - $start), 'new FlowStoreModule\(')).Count
Check 'store modules' ($modules -ge 50) "$modules registered"

# ---- 4. own TLS stack (live) ----
if (-not $SkipLive) {
    $probeExe = Join-Path $root 'tools\TlsProbe.Cli\bin\Release\net8.0\TlsProbe.Cli.exe'

    # Build only when the binary is missing. Running `dotnet build` immediately before invoking
    # the exe left this script unable to read the exe's output at all — exit code 0, empty
    # string, while the same exe prints normally when run from its own script or a shell.
    if (-not (Test-Path $probeExe)) {
        $null = & $dotnet build tools\TlsProbe.Cli -c Release -v q --nologo 2>&1
    }

    $outFile = Join-Path $env:TEMP 'cybersole-tlsprobe-out.txt'
    $errFile = Join-Path $env:TEMP 'cybersole-tlsprobe-err.txt'
    Remove-Item $outFile, $errFile -ErrorAction SilentlyContinue

    if (Test-Path $probeExe) {
        # The probe writes its own file. Two earlier attempts failed here:
        #   `& exe | Out-String` came back empty after `dotnet test` in the same session
        #   `Start-Process -RedirectStandardOutput` worked standalone but not after the tests
        # The probe itself was always fine — running it by hand printed
        # "HTTP 200  577 bytes  proto=h2  transport=own-tls12  alpn=h2" every time. So the fix
        # is not another stdio trick: the child writes the file, and this script only reads it.
        $null = & $probeExe --own example.com --out $outFile 2> $errFile
        $probeExit = $LASTEXITCODE
        $probeOut = if (Test-Path $outFile) { Get-Content $outFile -Raw } else { '' }
    } else {
        $probeOut = & $dotnet run --project tools\TlsProbe.Cli -c Release -- --own example.com 2>&1 | Out-String
        $probeExit = $LASTEXITCODE
    }

    if ($null -eq $probeOut) { $probeOut = '' }


    $ok = $probeOut -match 'HTTP 200' -and $probeOut -match 'own-tls12'

    # the detail used to be just the "HTTP ..." line, which came out empty when the probe failed
    # for an unrelated reason — leaving no way to tell "TLS broke" from "the probe did not run".
    $line = ($probeOut -split "`n" | Where-Object { $_ -match 'HTTP ' }) -join ' '
    if (-not $line) {
        $head = "$probeOut".Trim()
        if ($head.Length -gt 110) { $head = $head.Substring(0, 110) }
        $line = "probe exit=$probeExit, no HTTP line; said: " + ($head -replace '\s+', ' ')
    }

    if ($ok) {
        Check 'own TLS 1.2 + HTTP/2' $true "$line".Trim()
    } elseif ($probeExit -eq 0 -and -not ($probeOut -match 'HTTP ')) {
        # The process succeeded but produced nothing this script could read. That is a capture
        # problem in Windows PowerShell 5.1, not a TLS problem: running the same exe from an
        # interactive shell prints "HTTP 200 … transport=own-tls12" every time. Reporting it as
        # FAIL trained the reader to ignore a red line, which is worse than saying so.
        Warn 'own TLS 1.2 + HTTP/2' 'probe ran (exit 0) but its output was not capturable here; run tools\TlsProbe.Cli by hand'
    } else {
        Check 'own TLS 1.2 + HTTP/2' $false "$line".Trim()
    }
} else {
    Warn 'own TLS 1.2 + HTTP/2' 'skipped (-SkipLive)'
}

# ---- 5. contracts present ----
foreach ($doc in @('docs\PARITY.md', 'docs\WIRING.md', 'docs\VERDICT.md', 'docs\PLATFORM_VERIFICATION.md', 'docs\HISTORY.md', 'docs\ORIGINAL_ENDPOINTS.md', 'docs\NIKE_PARITY.md', 'docs\SESSION_STATE.md', 'docs\ORIGINAL_VIEWS.md', 'docs\IDB_EVIDENCE.md', 'docs\ENDPOINT_FAMILIES.md', 'docs\shopify_hosts.txt', 'docs\original_view_classes.txt', 'README.md')) {
    # These six passed with an empty detail for many rounds. Nothing was wrong with the checks —
    # a present file is a present file — but a PASS with no reason is indistinguishable from a
    # PASS whose reason could not be computed, which is the failure mode R171 was about. The size
    # is not a quality signal; it is evidence the check actually looked.
    $present = Test-Path $doc
    $size = if ($present) { (Get-Item $doc).Length } else { 0 }
    Check "doc $doc" $present $(if ($present) { "$size bytes" } else { 'missing' })
}

# ---- 6. mutation self-test, then the mutation check (only with -Full) ----
# A test that has never failed is not evidence. This breaks each guarded defect on purpose and
# confirms its guard notices; a guard that stays green is reported as FAIL, because "the test did
# not fail" is not the same as "the test works".
#
# The self-test runs first: it feeds the same script mutations with known outcomes, so a broken
# classifier is caught before its verdicts are trusted.
if ($Full -and (Test-Path 'tools\mutation-check.py')) {
    $py = 'D:\projects\IDA-pro\python311\python.exe'
    if (Test-Path $py) {
        if (Test-Path 'tools\mutation-self-test.py') {
            $self = & $py 'tools\mutation-self-test.py' 2>&1 | Out-String
            $correct = ([regex]::Matches($self, '\[ok  \]')).Count
            $wrong   = ([regex]::Matches($self, '\[FAIL\]')).Count
            if ($wrong -gt 0) {
                Check 'mutation self-test' $false "$correct right, $wrong wrong — the verdicts below cannot be trusted"
            } elseif ($correct -eq 0) {
                Warn 'mutation self-test' 'no cases ran'
            } else {
                Check 'mutation self-test' $true "$correct/$correct classified correctly"
            }
        } else {
            Warn 'mutation self-test' 'tools\mutation-self-test.py not found'
        }

        $mut = & $py 'tools\mutation-check.py' 2>&1 | Out-String
        # the loop prints "[guard fired] name" and the summary prints "guard fired  name", so a
        # bare count doubles everything; the bracket form appears once per mutation
        $decorative = ([regex]::Matches($mut, '\[GUARD IS DECORATIVE')).Count
        $fired      = ([regex]::Matches($mut, '\[guard fired\]')).Count
        $skipped    = ([regex]::Matches($mut, '\[skip\]')).Count
        # a mutation that fails to compile also exits non-zero, and that is not a catch: the guard
        # never ran. Three of the first thirteen did this and looked identical to a catch.
        $nocompile  = ([regex]::Matches($mut, '\[DID NOT COMPILE')).Count
        $summary    = "$fired fired, $decorative decorative, $nocompile did-not-compile, $skipped skipped"
        if ($decorative -gt 0) {
            Check 'mutation guards' $false $summary
        } elseif ($nocompile -gt 0) {
            Check 'mutation guards' $false "$summary — a mutation that does not build proves nothing"
        } elseif ($fired -eq 0) {
            Warn 'mutation guards' "no guard fired — the anchors no longer match: $summary"
        } else {
            Check 'mutation guards' $true $summary
        }
    } else {
        Warn 'mutation guards' "python not found at $py"
    }
} else {
    Warn 'mutation guards' 'skipped (use -Full)'
}

# ---- report ----
$results | Format-Table -AutoSize
$failedCount = ($results | Where-Object { $_.Result -eq 'FAIL' }).Count
if ($failedCount -eq 0) {
    Write-Host "`nVERDICT: all checks passed" -ForegroundColor Green
    exit 0
}

Write-Host "`nVERDICT: $failedCount check(s) failed" -ForegroundColor Red
exit 1
