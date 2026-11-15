import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tools\verify.ps1"
t = io.open(p, encoding="utf-8-sig").read()

# R109: the unit-test run now dies with StackOverflowException when its output is captured at
# `-v m` — the same filter at `-v q` passes 976 in 7 s. Minimal verbosity is enough here: the check
# only needs the exit code and the failure lines, and quieter output keeps the capture small.
old = ('$test = & $dotnet test tests\\Cybersole.Tests\\Cybersole.Tests.csproj --filter "Speed!=Slow" -v m --nologo 2>&1 | Out-String')
new = ('$test = & $dotnet test tests\\Cybersole.Tests\\Cybersole.Tests.csproj --filter "Speed!=Slow" -v q --nologo 2>&1 | Out-String')

if old not in t:
    raise SystemExit("unit-test invocation not found")
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8-sig", newline="").write(t)
print("unit-test run: -v m -> -v q")
