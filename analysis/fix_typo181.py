import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\WindowBaselineTests.cs"
t = io.open(p, encoding="utf-8").read()
t = t.replace('Assert.Contains!("G.top !== G", js);', 'Assert.Contains("G.top !== G", js);', 1)
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("typo fixed")
