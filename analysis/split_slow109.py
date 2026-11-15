import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tools\verify.ps1"
t = io.open(p, encoding="utf-8-sig").read()

# R109: the Kasada live group fetches and evaluates a real script; it is the slowest and most
# fragile part of the slow phase, and when it hangs it hides every other live result behind it.
# Split the phase so a hang there cannot mask the rest.
old_filter = '--filter "Speed=Slow" -v m --nologo 2>&1 | Out-String'
new_filter = '--filter "Speed=Slow&FullyQualifiedName!~Kasada" -v m --nologo 2>&1 | Out-String'

if t.count(old_filter) != 2:
    raise SystemExit("expected 2 slow-filter occurrences, found %d" % t.count(old_filter))
t = t.replace(old_filter, new_filter)

# add the Kasada group as its own check right after the slow check
anchor = "    Check 'slow tests (Speed=Slow)' $slowOk $slowDetail\n}"
addition = '''    Check 'slow tests (Speed=Slow)' $slowOk $slowDetail

    # ---- 2a-bis. the Kasada live group, on its own ----
    # It downloads and evaluates a real Kasada script, so it is an order of magnitude slower than
    # the rest of the live phase. As its own check, a hang or a host hiccup here is attributable to
    # this group instead of erasing every other live result behind it.
    $kasada = & $dotnet test tests\\Cybersole.Tests\\Cybersole.Tests.csproj `
        --filter "Speed=Slow&FullyQualifiedName~Kasada" -v m --nologo 2>&1 | Out-String
    $kasadaExit = $LASTEXITCODE
    $kasadaOk = ($kasadaExit -eq 0)
    $kasadaFails = ($kasada -split "`r?`n" |
                    Where-Object { $_ -match '^\\s*(失败|Failed|\\[xUnit\\.net.*FAIL)' } |
                    Select-Object -First 2) -join ' | '
    $kasadaDetail = if ($kasadaOk) { 'kasada live group green' }
                    elseif ($kasadaFails) { 'failed: ' + $kasadaFails }
                    else { "failed: exit $kasadaExit with no failing test line" }
    Check 'slow tests (kasada live)' $kasadaOk $kasadaDetail
}'''

if anchor not in t:
    raise SystemExit("Check anchor missing")
t = t.replace(anchor, addition, 1)

io.open(p, "w", encoding="utf-8-sig", newline="").write(t)
print("slow phase split: network group + kasada live group")
