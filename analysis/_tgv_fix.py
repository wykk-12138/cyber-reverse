import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\TaskGroupViewTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('namespace CsTests;\n\n', '')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('stray namespace removed')
