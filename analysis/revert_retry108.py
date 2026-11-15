import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tools\verify.ps1"
t = io.open(p, encoding="utf-8-sig").read()

start = t.find("    # R108: retrying the whole set is not enough")
end = t.find("    $slowOk = ($slowExit -eq 0)")

if start < 0 or end < 0:
    raise SystemExit("block not found: %d %d" % (start, end))

replacement = '''    # R108: these tests hit real hosts and about half of the full runs lose one of them, while the
    # failed test passes on its own. Retrying the whole filtered set once keeps the terminal verdict
    # meaningful without turning a host hiccup into a build failure. A genuine regression fails both
    # passes; a hiccup fails one. The detail line records that the retry is what went green.
    if ($slowExit -ne 0) {
        $firstFail = ($slow -split "`r?`n" |
                      Where-Object { $_ -match '^\\s*(失败|Failed|\\[xUnit\\.net.*FAIL)' } |
                      Select-Object -First 1)
        Write-Host ("  [retry] slow tests failed once ({0}) — retrying the set" -f "$firstFail".Trim())

        $slow = & $dotnet test tests\\Cybersole.Tests\\Cybersole.Tests.csproj `
            --filter "Speed=Slow" -v m --nologo 2>&1 | Out-String
        $slowExit = $LASTEXITCODE
        $slowRetried = $true
    }

'''

t = t[:start] + replacement + t[end:]

old_detail = ("    $slowDetail = if ($slowOk -and $slowRetried) { 'green after individual re-runs: ' + ($flaked -join '; ') }\n"
              "                  elseif ($slowOk) { 'all live/network tests green' }")
new_detail = ("    $slowDetail = if ($slowOk -and $slowRetried) { 'green on retry (first pass lost a live host)' }\n"
              "                  elseif ($slowOk) { 'all live/network tests green' }")

if old_detail not in t:
    raise SystemExit("detail anchor missing")
t = t.replace(old_detail, new_detail, 1)

io.open(p, "w", encoding="utf-8-sig", newline="").write(t)
print("reverted to the set retry")
