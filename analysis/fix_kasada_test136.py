import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\KasadaStrategyTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '        Assert.Contains("Nike-Kasada-Version", NikeHeaders.Identifiers);'
new = '        Assert.Equal("Nike-Kasada-Version", NikeHeaders.KasadaVersion);'

if old not in t:
    raise SystemExit("nike header anchor missing")
t = t.replace(old, new, 1)

if "using Cybersole.Stores.Flows;" not in t:
    t = "using Cybersole.Stores.Flows;\n" + t

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("reference fixed")
