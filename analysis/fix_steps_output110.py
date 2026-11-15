import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tools\verify-steps.ps1"
t = io.open(p, encoding="utf-8").read()

# Write-Host, not pipeline output: the caller consumes the function's return value as a boolean, and
# anything else it emits is swallowed with it.
old = '''    "{0,-22} {1}  {2}" -f $s.Name, $(if ($ok) { 'PASS' } else { 'FAIL' }), $detail
    return $ok'''

new = '''    Write-Host ("{0,-22} {1}  {2}" -f $s.Name, $(if ($ok) { 'PASS' } else { 'FAIL' }), $detail)
    return $ok'''

if old not in t:
    raise SystemExit("print anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("step output now goes to the console")
