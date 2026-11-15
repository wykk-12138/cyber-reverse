import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\NavOrderTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        Assert.Equal(49, NavOrder.Navigator.Count);'''

new = '''        // 50, not 49: the comment in R159 said 49 and the list itself has fifty entries — the sort of number
        // that is worth taking from the data rather than from a sentence about the data.
        Assert.Equal(50, NavOrder.Navigator.Count);'''

if old not in t:
    raise SystemExit("count anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the count comes from the list")
