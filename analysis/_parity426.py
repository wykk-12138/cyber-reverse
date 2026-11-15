import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\OriginalViewClassParityTests.cs"
lines = io.open(p, encoding='utf-8').read().split('\n')
for i, line in enumerate(lines):
    if 'Assert.Equal(12, renamed);' in line:
        lines[i] = '        Assert.Equal(11, renamed);      // R423: MonitorView now exists by name, so it left this bucket'
        print('renamed 12 -> 11')
        break
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
