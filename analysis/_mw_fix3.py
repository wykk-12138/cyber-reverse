import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\UnreachedUiTypesTests.cs'
lines = io.open(p, encoding='utf-8').read().splitlines()
out = []
for line in lines:
    if line.strip() == ',':
        continue
    out.append(line)
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(out) + '\n')
print('stray comma line removed')
