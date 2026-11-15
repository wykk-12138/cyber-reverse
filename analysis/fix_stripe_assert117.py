import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\DemandwareStepMapTests.cs"
t = io.open(p, encoding="utf-8").read()

old = 'Assert.Contains(DemandwareStepMap.StripeFinding, "no Stripe");'
new = 'Assert.Contains("no Stripe", DemandwareStepMap.StripeFinding, System.StringComparison.Ordinal);'

if old not in t:
    raise SystemExit("anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("assertion order fixed")
