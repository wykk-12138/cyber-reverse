import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\LiveSchemaPinsTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('Cybersole.Core.AppPaths.Json.Default', 'Cybersole.Core.Store.Json.Default')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('namespace fixed')
