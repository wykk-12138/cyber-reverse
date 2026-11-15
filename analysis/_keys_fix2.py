import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\KeyBindChordTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('binds.DeleteSelected', 'binds.Delete').replace('binds.CloneSelected', 'binds.Clone').replace('binds.CopySelected', 'binds.Copy')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('property names matched to the model')
