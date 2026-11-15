import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\EndpointEvidenceRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()
add = '''
    [Fact]
    public void EveryUnbackedEndpointSaysSoInItsFile()
    {
        // R294: the marker is the point — a path with no image evidence must not look like an evidenced one when you are
        // reading the flow it lives in.
        var root = Root();
        foreach (var file in Unbacked.Select(u => u.File).Distinct())
        {
            var full = Path.Combine(root, file.Replace('/', Path.DirectorySeparatorChar));
            var text = File.ReadAllText(full);
            _out.WriteLine(file + (text.Contains("inferred: no image evidence", StringComparison.Ordinal) ? ": marked" : ": MISSING"));
            Assert.Contains("inferred: no image evidence", text, StringComparison.Ordinal);
        }
    }

'''
marker = '    private static string Root()'
assert marker in t
t = t.replace(marker, add + marker, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('marker assertion added')
