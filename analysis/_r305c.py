import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\EndpointEvidenceRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()

old = '''        var root = Root();
        foreach (var file in Sent.Concat(DocumentedOnly).Select(u => u.File).Distinct())
        {
            var full = Path.Combine(file, file);
        }'''
# locate the marker test body by its comment line
start = t.index('    [Fact]\n    public void EveryUnbackedEndpointSaysSoInItsFile()')
end = t.index('    private static string Root()')
new = '''    [Fact]
    public void EveryUnbackedEndpointSaysSoOnItsOwnLine()
    {
        // R305 correction: the first version of this test only asked whether the FILE contained the marker, and a
        // mutation-check pass proved it decorative — GoatFlow.cs carries two markers (R294 and R298), so deleting one
        // left the other behind and the test stayed green. The binding is now per path: the marker must sit on a line
        // that also mentions that path.
        var root = Root();
        foreach (var (path, file) in Sent.Concat(DocumentedOnly).Distinct())
        {
            var full = Path.Combine(root, file.Replace('/', Path.DirectorySeparatorChar));
            var lines = File.ReadAllLines(full);
            var bound = lines.Any(l => l.Contains(path, StringComparison.Ordinal)
                                       && l.Contains("inferred: no image evidence", StringComparison.Ordinal));

            _out.WriteLine($"{path} in {file}: bound={bound}");
            Assert.True(bound, $"no 'inferred: no image evidence' marker on the line that uses {path} in {file}");
        }
    }

'''
t = t[:start] + new + t[end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('marker test is now per path')
