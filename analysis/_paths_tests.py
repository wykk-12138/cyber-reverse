import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\LiveSchemaPinsTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void EverythingTheReplicaWritesStaysUnderItsOwnDataRoot()
    {
        // R405: R387 let the replica write into the ORIGINAL's %APPDATA%\\Cybersole. This test pins the consequence: every
        // writable path must sit under DataRoot (the replica's own directory), and the vendor's local install is not
        // reachable as a write target at all.
        var root = Cybersole.Core.Store.AppPaths.DataRoot.TrimEnd('\\\\', '/');

        foreach (var path in Cybersole.Core.Store.AppPaths.WritablePaths)
        {
            _out.WriteLine(path);
            Assert.StartsWith(root, path, StringComparison.OrdinalIgnoreCase);
        }

        Assert.DoesNotContain(
            Cybersole.Core.Store.AppPaths.LocalRoot,
            Cybersole.Core.Store.AppPaths.WritablePaths,
            StringComparer.OrdinalIgnoreCase);
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('writable-paths guard appended')
