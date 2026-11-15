import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tools\verify-steps.ps1"
t = io.open(p, encoding="utf-8").read()

old = '''function Invoke-Step($s) {
    $out = & $s.Run
    $code = $LASTEXITCODE'''

new = '''function Invoke-Step($s) {
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
'''

if old not in t:
    raise SystemExit("anchor missing")
if "[retry] {0} failed once" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
    print("slow steps retry once")
