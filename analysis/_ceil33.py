import io, re
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\BindingGapRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()
t = re.sub(r'private const int MaxRealGap = \d+;', 'private const int MaxRealGap = 33;', t)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
p2 = r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('当前 32 = 1 可做 + 31 结构', '当前 33 = 2 可做 + 31 结构')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('both set to the measured 33')
