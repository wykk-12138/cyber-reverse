import io, re
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\BindingGapRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()
t = re.sub(r'private const int MaxRealGap = \d+;', 'private const int MaxRealGap = 19;', t)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
p2 = r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('当前 26 = 0 可做 + 26 结构（A 类清零；R312 ComboBoxEdit、R314 ProfileCsvRow）',
                '当前 19 = 0 可做 + 19 结构（A 类清零；R312 ComboBoxEdit、R314 ProfileCsvRow、R317 行家族）')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('ceiling 19 + backlog updated')
