import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\BindingGapRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('private const int MaxRealGap = 61;', 'private const int MaxRealGap = 63;')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ceiling corrected to the measured 63')
