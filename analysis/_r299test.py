import io, re
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\EndpointEvidenceRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()

# replace the single Unbacked table with two tables, split by whether the path is actually sent
start = t.index('    private static readonly (string Path, string File)[] Unbacked =')
end = t.index('    private const int Ceiling = 22;')
new_tables = '''    /// <summary>Paths the code actually sends, with no pool evidence (R299 split).</summary>
    private static readonly (string Path, string File)[] Sent =
    {
        ("/account/recover", "src/Cybersole.Stores/Flows/StoreFlow.cs"),
        ("/account/verify", "src/Cybersole.Stores/Flows/MagentoFlow.cs"),
        ("/api/checkout/v1/basket/{basketId}", "src/Cybersole.Stores/Flows/FarfetchFlow.cs"),
        ("/api/checkout/v1/basket/{basketId}/place-order", "src/Cybersole.Stores/Flows/FarfetchFlow.cs"),
        ("/api/checkout/v1/basket/{basketId}/shipping", "src/Cybersole.Stores/Flows/FarfetchFlow.cs"),
        ("/api/preorder/entry", "src/Cybersole.Stores/Flows/RetailFlows.cs"),
        ("/api/stock", "src/Cybersole.Stores/Flows/PopMartEndpoints.cs"),
        ("/collections/new-releases", "src/Cybersole.Stores/Flows/MagentoFlow.cs"),
        ("/rest/V1/carts/mine/totals", "src/Cybersole.Stores/Flows/MagentoFlow.cs"),
        ("/v1/buys", "src/Cybersole.Stores/Flows/GoatFlow.cs"),
    };

    /// <summary>
    /// Paths that appear only in a doc comment — a claim about the store, not a request the replica makes. R299: this
    /// split matters, because "/api/beast" reads like an invented request and is in fact a documented observation.
    /// </summary>
    private static readonly (string Path, string File)[] DocumentedOnly =
    {
        ("/api/basket/v1/items", "src/Cybersole.Stores/Flows/FarfetchFlow.cs"),
        ("/api/beast", "src/Cybersole.Stores/Flows/BstnFlow.cs"),
        ("/api/checkout/submit", "src/Cybersole.Stores/Flows/RetailFlows.cs"),
        ("/api/order/submit", "src/Cybersole.Stores/Flows/PopMartEndpoints.cs"),
        ("/api/search", "src/Cybersole.Stores/Flows/ScheelsFlow.cs"),
        ("/api/v2/shop/countries", "src/Cybersole.Stores/Flows/HbxFlow.cs"),
        ("/view/resources/getUserInfo", "src/Cybersole.Stores/Flows/HybrisFlow.cs"),
    };

'''
t = t[:start] + new_tables + t[end:]

# rewrite the assertions to use the split
t = t.replace('''    private const int Ceiling = 22;''', '''    private const int SentCeiling = 10;
    private const int DocOnlyCeiling = 7;''', 1)
t = t.replace('''    [Fact]
    public void TheUnbackedListDoesNotGrow()
    {
        var distinct = Unbacked.Select(u => u.Path).Distinct().Count();
        _out.WriteLine($"unbacked entries {Unbacked.Length}, distinct paths {distinct}, ceiling {Ceiling}");
        Assert.True(distinct <= Ceiling, $"unbacked endpoints grew to {distinct}");
    }''', '''    [Fact]
    public void NeitherListGrows()
    {
        _out.WriteLine($"sent={Sent.Length}/{SentCeiling} documented-only={DocumentedOnly.Length}/{DocOnlyCeiling}");
        Assert.True(Sent.Select(s => s.Path).Distinct().Count() <= SentCeiling);
        Assert.True(DocumentedOnly.Select(s => s.Path).Distinct().Count() <= DocOnlyCeiling);
    }''', 1)
t = t.replace('        foreach (var (path, file) in Unbacked.Distinct())',
              '        foreach (var (path, file) in Sent.Concat(DocumentedOnly).Distinct())', 1)
t = t.replace('        foreach (var file in Unbacked.Select(u => u.File).Distinct())',
              '        foreach (var file in Sent.Concat(DocumentedOnly).Select(u => u.File).Distinct())', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ratchet split into sent / documented-only')
