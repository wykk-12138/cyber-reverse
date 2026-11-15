import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\XamlBindingTableTests.cs'
t = io.open(p, encoding='utf-8').read()
add = '''
    [Fact]
    public void TheProxyViewsBoundNamesExistAndTheButtonsCallThem()
    {
        // R226: the original binds these on ProxyView; the replica had the behaviour inside inline lambdas.
        var source = View("Proxies/ProxyView.cs");

        foreach (var name in new[]
                 {
                     "AddProxies", "ClearAll", "CopyProxies", "CloneProxies", "DeleteProxies", "TestProxies",
                 })
        {
            Assert.Contains("public void " + name + "(", source);
        }

        // and they are live: the buttons go through them, not around them
        Assert.Contains("UiKit.Button(\\"Add Proxies\\", () => AddProxies(target))", source);
        Assert.Contains("UiKit.Button(\\"Clear All\\", () => ClearAll(target))", source);
    }

    [Fact]
    public void TheDocExplainsTheTwoScopesAndTheNoise()
    {
        var doc = File.ReadAllText(Path.Combine(Root(), "docs", "XAML_BINDINGS.md"));
        Assert.Contains("两种口径", doc, System.StringComparison.Ordinal);
        Assert.Contains("per-file", doc, System.StringComparison.Ordinal);
        Assert.Contains("whole-source", doc, System.StringComparison.Ordinal);

        // the generic instantiation members are called out as compiler noise, not design
        Assert.Contains("HasMultiple_", doc, System.StringComparison.Ordinal);
        Assert.Contains("噪音", doc, System.StringComparison.Ordinal);

        // and the tool that produces the numbers ships with the repo
        Assert.True(File.Exists(Path.Combine(Root(), "tools", "bind_diff.py")));
    }
}
'''
t = t.rstrip()
assert t.endswith('}')
t = t[:t.rfind('}')] + add
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('two tests appended')
