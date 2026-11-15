import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\WindowOrderTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        Assert.Contains("last statement", WindowOrder.BaselineRule.Replace("the snapshot", "the snapshot"));'''
new = '''        Assert.Contains("include everything installed above", WindowOrder.BaselineRule);'''
if old not in t:
    raise SystemExit("rule assertion anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("assertion follows the actual sentence")
