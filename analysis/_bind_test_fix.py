import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\XamlBindingTableTests.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('''        Assert.True(types.Count > 150, "the table should cover the whole UI, not a corner");
        Assert.True(members > 1000);''',
'''        Assert.True(types.Count > 150, "the table should cover the whole UI, not a corner");
        // 819 distinct member names; 1457 getter/setter descriptors before de-duplication
        Assert.True(members > 700, "the table should be the whole binding surface, not a sample");''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('assertion corrected to unique-member count')
