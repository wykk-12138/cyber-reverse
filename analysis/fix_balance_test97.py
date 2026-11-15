import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\ShopifyGraphQlTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    /// <summary>Balanced braces: a selection set is a tree, and one missing bracket breaks it whole.</summary>
    [Fact]
    public void TheDocumentsAreBalanced()
    {
        foreach (var (name, text) in new[]
                 {
                     ("selection", ShopifyGraphQl.CartSelection),
                     ("mutation", ShopifyGraphQl.CartLinesUpdate),
                 })
        {
            var open = text.Count(c => c == '{');
            var close = text.Count(c => c == '}');
            _out.WriteLine($"{name}: {open} open / {close} close");

            Assert.Equal(open, close);
        }
    }'''

new = '''    /// <summary>
    /// Brace accounting. The mutation is a whole document so its braces balance (12/12). The
    /// selection set is a <b>fragment</b>: the pool stores it starting at <c>"){id,checkoutUrl…"</c>
    /// — the <c>)</c> closes the <c>cart(…)</c> call, the selection set opens, and the document's own
    /// closing brace is included while its opening brace is not. So 12 open / 13 close is correct,
    /// and asserting equality here would force someone to "fix" a faithful copy.
    /// </summary>
    [Fact]
    public void TheDocumentBracesAreAccountedFor()
    {
        var selectionOpen = ShopifyGraphQl.CartSelection.Count(c => c == '{');
        var selectionClose = ShopifyGraphQl.CartSelection.Count(c => c == '}');
        var mutationOpen = ShopifyGraphQl.CartLinesUpdate.Count(c => c == '{');
        var mutationClose = ShopifyGraphQl.CartLinesUpdate.Count(c => c == '}');

        _out.WriteLine($"selection: {selectionOpen}/{selectionClose}  mutation: {mutationOpen}/{mutationClose}");

        Assert.Equal(12, selectionOpen);
        Assert.Equal(13, selectionClose);       // +1: the fragment drops the operation's opening brace
        Assert.Equal(mutationOpen, mutationClose);

        // the fragment really starts where the pool says it does
        Assert.StartsWith("\\"){id,checkoutUrl", ShopifyGraphQl.CartSelection);
    }'''

if old not in t:
    raise SystemExit("balance block anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("balance test rewritten")
