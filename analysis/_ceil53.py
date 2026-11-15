import io, re
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\BindingGapRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()
t = re.sub(r'private const int MaxRealGap = \d+;', 'private const int MaxRealGap = 53;', t)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ceiling -> 53 (from the measurement above)')
