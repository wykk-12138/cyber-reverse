import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\BindingGapRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('private const int MaxRealGap = 28;',
              'private const int MaxRealGap = 96;   // R249: re-baselined after the matcher stopped reading comments as code')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ceiling re-baselined to 96')
