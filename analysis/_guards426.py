import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\DocsConsistencyTests.cs"
t = io.open(p, encoding='utf-8').read()
old = '''        // any "<n> 条" followed by wording about the error texts
        var claims = Regex.Matches(doc, @"(\\d+)\\s*条(?:：|逐字|错误文案|文案|错误)")'''
new = '''        // R426: only phrases that are actually about the error catalogue — the old pattern also caught "39 条文案" and
        // "8 条逐字" from the copy-table rounds and failed four claims that were never about ErrorCatalog.
        var claims = Regex.Matches(doc, @"(\\d+)\\s*条(?:错误文案|错误文本)")'''
assert old in t, 'pattern not found'
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('guard narrowed to error-specific wording')

# the view-class parity constant follows the fact: 75 -> 76 same
p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\OriginalViewClassParityTests.cs"
t2 = io.open(p2, encoding='utf-8').read()
import re
m = re.search(r'Assert\.Equal\((7[0-9]), same', t2)
print('before:', m.group(0) if m else 'not found')
if m:
    t2 = t2.replace(m.group(0), 'Assert.Equal(76, same', 1)
    io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
    print('same 75 -> 76')
