import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tools\verify-steps.ps1"
t = io.open(p, encoding="utf-8").read()

# The docs step is a Test-Path sweep with no external process, so $LASTEXITCODE is $null there and
# the step read as FAIL. Judge it by its own output instead of by an exit code it never sets.
old = '''    $out = & $s.Run
    $code = $LASTEXITCODE
    $ok = ($code -eq 0)
    if (-not $ok -and ($out -match 'error CS')) { $ok = $false }'''

new = '''    $out = & $s.Run
    $code = $LASTEXITCODE
    $ok = if ($null -eq $code) { -not ($out -match 'missing:') } else { $code -eq 0 }
    if ($out -match 'error CS') { $ok = $false }'''

if old not in t:
    raise SystemExit("judge anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("steps: docs judged by its own output")
