import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\LiveSchemaPinsTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheReplicaNeverWritesIntoTheOriginalsDataDirectory()
    {
        // R387: this was true until today, which both endangered the user's live configuration and made every
        // "does my file match the original's?" check circular.
        var replica = Cybersole.Core.Store.AppPaths.DataRoot;
        var original = Cybersole.Core.Store.AppPaths.OriginalDataRoot;

        _out.WriteLine("replica:  " + replica);
        _out.WriteLine("original: " + original);

        Assert.NotEqual(
            original.TrimEnd('\\\\', '/'),
            replica.TrimEnd('\\\\', '/'),
            StringComparer.OrdinalIgnoreCase);
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('guard test appended')
