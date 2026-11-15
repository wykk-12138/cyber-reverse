import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\BindingGapRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('private const int MaxRealGap = 64;', 'private const int MaxRealGap = 61;')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ceiling 64 -> 61')
