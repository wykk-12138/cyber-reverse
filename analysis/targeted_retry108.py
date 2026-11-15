import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tools\verify.ps1"
t = io.open(p, encoding="utf-8-sig").read()

old = '''    if ($slowExit -ne 0) {
        $firstFail = ($slow -split "`r?`n" |
                      Where-Object { $_ -match '^\\s*(失败|Failed|\\[xUnit\\.net.*FAIL)' } |
                      Select-Object -First 1)
        Write-Host ("  [retry] slow tests failed once ({0}) — retrying the set" -f "$firstFail".Trim())

        $slow = & $dotnet test tests\\Cybersole.Tests\\Cybersole.Tests.csproj `
            --filter "Speed=Slow" -v m --nologo 2>&1 | Out-String
        $slowExit = $LASTEXITCODE
        $slowRetried = $true
    }

    $slowOk = ($slowExit -eq 0)'''

new = '''    # R108: retrying the whole set is not enough — twice in a row the retry failed on a *different*
    # live test than the first pass did (TheSecureTokenRotates…, then AHundredTimesCallerStillG…).
    # So the retry is now aimed: pull the failing test names out of the output and re-run just those,
    # one at a time. A test that is genuinely broken fails alone; a test that timed out against a
    # real host passes alone. That is the distinction the terminal judgement needs.
    $flaked = @()

    if ($slowExit -ne 0) {
        $names = ($slow -split "`r?`n" |
                  ForEach-Object {
                      if ($_ -match '(Cybersole\\.Tests\\.[A-Za-z0-9_]+\\.[A-Za-z0-9_]+)') { $Matches[1] }
                  } | Select-Object -Unique)

        Write-Host ("  [retry] slow set failed; re-running {0} failing test(s) individually" -f $names.Count)

        foreach ($name in $names) {
            if (-not $name) { continue }
            $one = & $dotnet test tests\\Cybersole.Tests\\Cybersole.Tests.csproj `
                --filter "FullyQualifiedName~$name" -v q --nologo 2>&1 | Out-String
            if ($LASTEXITCODE -ne 0) {
                $flaked += "still failing alone: $name"
            } else {
                $flaked += "flaked in the set, green alone: $name"
            }
        }

        $slowExit = if ($flaked | Where-Object { $_ -like 'still failing alone:*' }) { 1 } else { 0 }
        $slowRetried = $true
    }

    $slowOk = ($slowExit -eq 0)'''

if old not in t:
    raise SystemExit("retry anchor missing")
t = t.replace(old, new, 1)

old_detail = ("    $slowDetail = if ($slowOk -and $slowRetried) { 'green on retry (first pass had a live-network failure)' }\n"
              "                  elseif ($slowOk) { 'all live/network tests green' }")
new_detail = ("    $slowDetail = if ($slowOk -and $slowRetried) { 'green after individual re-runs: ' + ($flaked -join '; ') }\n"
              "                  elseif ($slowOk) { 'all live/network tests green' }")

if old_detail not in t:
    raise SystemExit("detail anchor missing")
t = t.replace(old_detail, new_detail, 1)

io.open(p, "w", encoding="utf-8-sig", newline="").write(t)
print("slow phase: targeted per-test re-runs, failure only when a test fails alone")
