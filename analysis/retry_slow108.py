import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tools\verify.ps1"
t = io.open(p, encoding="utf-8-sig").read()

old = '''if ($Full) {
    $slow = & $dotnet test tests\\Cybersole.Tests\\Cybersole.Tests.csproj `
        --filter "Speed=Slow" -v m --nologo 2>&1 | Out-String
    # R63: read the exit code once, immediately. This check failed in the suite twice and passed
    # alone every time — and with only "no failure line in the output" to go on, a network hiccup
    # and a killed process were indistinguishable. Keeping the code and the tail makes the next
    # occurrence diagnosable instead of mysterious.
    $slowExit = $LASTEXITCODE
    $slowOk = ($slowExit -eq 0)'''

new = '''if ($Full) {
    # R108: these tests hit real hosts, and a single one of them fails in roughly every other full
    # run while passing on its own (six different tests over four rounds, each green standalone).
    # That made the terminal judgement depend on which host hiccuped, so the phase now retries the
    # whole filtered set once. A genuine regression fails both times; a hiccup fails once.
    $slow = & $dotnet test tests\\Cybersole.Tests\\Cybersole.Tests.csproj `
        --filter "Speed=Slow" -v m --nologo 2>&1 | Out-String
    # R63: read the exit code once, immediately. This check failed in the suite twice and passed
    # alone every time — and with only "no failure line in the output" to go on, a network hiccup
    # and a killed process were indistinguishable. Keeping the code and the tail makes the next
    # occurrence diagnosable instead of mysterious.
    $slowExit = $LASTEXITCODE
    $slowRetried = $false

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

    $slowOk = ($slowExit -eq 0)'''

if old not in t:
    raise SystemExit("slow-tests anchor missing")
t = t.replace(old, new, 1)

# the detail line should say when a retry rescued the run
old_detail = "    $slowDetail = if ($slowOk) { 'all live/network tests green' }"
new_detail = ("    $slowDetail = if ($slowOk -and $slowRetried) { 'green on retry (first pass had a live-network failure)' }\n"
              "                  elseif ($slowOk) { 'all live/network tests green' }")

if old_detail not in t:
    raise SystemExit("detail anchor missing")
t = t.replace(old_detail, new_detail, 1)

io.open(p, "w", encoding="utf-8-sig", newline="").write(t)
print("slow phase: one retry + retry-aware detail")
