import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\KeyBindChordTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('binds.AddProfile', 'binds.Add')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('billing property fixed')
