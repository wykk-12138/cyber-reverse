import io, re
# the backlog doc is now derived from the tool; make the ratchet test check the two agree on the numbers
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\BindingGapRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()
add = '''
    [Fact]
    public void TheBacklogDocQuotesTheCeiling()
    {
        var doc = File.ReadAllText(Path.Combine(Root(), "docs", "BINDING_BACKLOG.md"));

        // the doc's headline number and the ratchet's ceiling must be the same number, or one of them is stale
        Assert.Contains($"当前 {MaxRealGap} =", doc, System.StringComparison.Ordinal);
        _out.WriteLine("backlog doc and ratchet agree on " + MaxRealGap);
    }
}
'''
t = t.rstrip()
assert t.endswith('}')
t = t[:t.rfind('}')] + add
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ratchet now cross-checks the backlog doc')
