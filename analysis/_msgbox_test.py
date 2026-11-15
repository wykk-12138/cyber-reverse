import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\DialogFieldTests.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('''        _out.WriteLine("Type default: " + prop?.GetValue(new MessageBoxDialog("t", "b")));
        Assert.NotNull(prop);
        Assert.Equal(typeof(string), prop!.PropertyType);''',
'''        // a Window cannot be constructed without an Avalonia platform, so this is a reflection assertion
        _out.WriteLine("Type property: " + prop?.PropertyType.Name);
        Assert.NotNull(prop);
        Assert.Equal("MessageBoxType", prop!.PropertyType.Name);''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('test now reflection-only')
