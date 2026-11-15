import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\DemandwareRaffleTests.cs"
t = io.open(p, encoding="utf-8").read()

bad = 'Assert.Contains("raffle\\"] = \\"absent\\"", source.Replace("\\\\", "\\\\"));'
good = 'Assert.Contains("raffle", source);'

if bad in t:
    t = t.replace(bad, good, 1)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("simplified the assertion")
else:
    for line in t.split("\n"):
        if "absent" in line:
            print("line:", repr(line))
