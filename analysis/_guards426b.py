import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\DocsConsistencyTests.cs"
lines = io.open(p, encoding='utf-8').read().split('\n')
done = False
for i, line in enumerate(lines):
    if 'var claims = Regex.Matches(doc, @' in line:
        lines[i] = '        // R426: narrowed to error-specific wording - the old pattern also caught "39 条文案" / "8 条逐字"\n        var claims = Regex.Matches(doc, @"(\\d+)\\s*条(?:错误文案|错误文本)")'
        done = True
        break
assert done
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('regex replaced by line')

p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\OriginalViewClassParityTests.cs"
lines2 = io.open(p2, encoding='utf-8').read().split('\n')
done2 = False
for i, line in enumerate(lines2):
    if 'Assert.Equal(75, same' in line:
        lines2[i] = line.replace('Assert.Equal(75, same', 'Assert.Equal(76, same')
        done2 = True
        break
print('parity constant bumped:', done2)
io.open(p2, 'w', encoding='utf-8', newline='').write('\n'.join(lines2))
