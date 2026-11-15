import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceRuntimeTests.cs"
t = io.open(p, encoding="utf-8").read()

old = 'await bridge.NavigateAsync("about:blank");'
new = 'await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");'

if old not in t:
    raise SystemExit("navigate anchor missing")
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)

# and the probe navigates the same way, so its numbers mean the same thing
q = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\ProbeDiagnostics.cs"
s = io.open(q, encoding="utf-8").read()
s = s.replace('await bridge.NavigateAsync("about:blank");',
              'await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");', 1)
io.open(q, "w", encoding="utf-8", newline="").write(s)
print("about:blank does not run the new-document script; a real document does")
