import io, re
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\BindingGapRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()
t = re.sub(r'private const int MaxRealGap = \d+;', 'private const int MaxRealGap = 58;', t)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ceiling set to 58 (measured, not guessed)')
