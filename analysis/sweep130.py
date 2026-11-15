import io

p = r"D:\projects\cyber-reverse\replica\tools\verify-steps.ps1"
t = io.open(p, encoding="utf-8").read()

old = """if ($Step -gt 0) {"""

new = """# R130: every browser launch leaves a cyb-chromium-* profile in %TEMP% (5 MB each, 1.8 GB after a
# few hundred runs). Sweep them before the run so the cost never accumulates.
$sweep = Join-Path $PSScriptRoot 'clean-temp.ps1'
if (Test-Path $sweep) {
    try { & powershell -NoProfile -ExecutionPolicy Bypass -File $sweep | Out-Null } catch { }
}

if ($Step -gt 0) {"""

if old not in t:
    raise SystemExit("step branch not found")
if "clean-temp.ps1" in t:
    print("already sweeps")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
    print("verify sweeps temp profiles before running")
