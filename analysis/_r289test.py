import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\StoreFlowSourceTests.cs'
t = io.open(p, encoding='utf-8').read()

start = t.index('    [Fact]\n    public void TheLiteralFlowsAreMarkedLiteral()')
end = t.index('    [Fact]\n    public void TheDistinctionIsWrittenDown()')
new = '''    [Fact]
    public void EveryFlowIsLiteralBackedAndNamesItsLiteral()
    {
        // R289: the last two flows were assembled from evidence and are now literal-backed as well — nike from two d__
        // literals of one class (0x03385576 + 0x0338562c), johnlewis from one d__ literal plus the lambda row that names
        // the two steps R112 had to deduce by hand (0x0338a655 + 0x0338af47). So the endpoint bucket is empty, and the
        // test that used to require members in it now requires the opposite: nothing is left unverified.
        foreach (var flow in StoreFlowSteps.All)
            _out.WriteLine($"{flow.Store}: {flow.Source} ({flow.Count} steps)");

        var endpoints = StoreFlowSteps.All.Where(f => f.Source == StoreFlowSteps.FlowSource.Endpoint)
            .Select(f => f.Store).ToList();
        var literal = StoreFlowSteps.All.Where(f => f.Source == StoreFlowSteps.FlowSource.Literal)
            .Select(f => f.Store).OrderBy(n => n, System.StringComparer.Ordinal).ToList();

        _out.WriteLine("endpoint-derived: " + (endpoints.Count == 0 ? "(none)" : string.Join(", ", endpoints)));
        Assert.Empty(endpoints);
        Assert.Equal(8, literal.Count);
        Assert.Contains("nike", literal);
        Assert.Contains("johnlewis", literal);
        Assert.Contains("popmart", literal);
        Assert.Contains("structure-token-single", literal);
    }

'''
t = t[:start] + new + t[end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('source test rewritten for the all-literal state')
