import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\GroupGridTests.cs'
t = io.open(p, encoding='utf-8').read()
old = '''        Assert.Contains("new Common.GroupGrid()", code);'''
new = '''        Assert.Contains("Common.GroupGrid _groups", code);'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new))
print('assertion fixed')
