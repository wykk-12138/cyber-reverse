import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tools\verify.ps1"
t = io.open(p, encoding="utf-8-sig").read()

# R110: the same `-v m` capture that crashed the unit-test phase also applies to the two slow
# phases. `-v q` is enough for an exit code and a failure line, and it keeps the capture small.
before = t.count("-v m")
t = t.replace("-v m", "-v q")
after = t.count("-v m")

io.open(p, "w", encoding="utf-8-sig", newline="").write(t)
print("replaced %d '-v m' occurrences, %d left" % (before, after))
