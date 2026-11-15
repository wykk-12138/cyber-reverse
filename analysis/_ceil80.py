import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\BindingGapRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('private const int MaxRealGap = 96;', 'private const int MaxRealGap = 80;')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ceiling 96 -> 80')
