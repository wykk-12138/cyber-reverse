import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\KeyBindChordTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('using Cybersole.Core.Models;', 'using Cybersole.Core.Models;\nusing Cybersole.Core.Settings;')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('using Cybersole.Core.Settings added')
