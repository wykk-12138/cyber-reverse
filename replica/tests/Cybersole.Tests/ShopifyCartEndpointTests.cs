using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 96: the Shopify cart vocabulary, read out of the 5.18.32 image.
///
/// <para>
/// Every literal in the image containing <c>cart/</c> was dumped and read. For Shopify the set is
/// exactly two:
/// </para>
///
/// <code>
/// cart/add.js
/// cart/update.js
/// </code>
///
/// <para>
/// <b>Neither <c>cart/change.js</c> nor <c>cart/clear.js</c> occurs anywhere in the image.</b> The
/// replica used both: <c>ShopifyFlow</c> posted quantity changes to <c>/cart/change.js</c>, and
/// <c>StoreFlow</c> cleared the cart with <c>/cart/clear.js</c> and changed it with
/// <c>/cart/change.js</c>. On a real storefront those two routes exist — Shopify documents them —
/// but this binary does not call them, and 1:1 means matching the binary, not the vendor docs.
/// </para>
///
/// <para>
/// Both are now <c>/cart/update.js</c> (a clear is an update to zero quantities), which is the
/// endpoint the image actually uses.
/// </para>
/// </summary>
public sealed class ShopifyCartEndpointTests
{
    private readonly ITestOutputHelper _out;

    public ShopifyCartEndpointTests(ITestOutputHelper output) => _out = output;

    private static string Source(string file)
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;

        return File.ReadAllText(Path.Combine(dir!.FullName, "src", "Cybersole.Stores", "Flows", file));
    }

    /// <summary>No source file still posts to the two routes the image does not contain.</summary>
    [Fact]
    public void NoFlowUsesChangeOrClear()
    {
        var flows = Directory.GetFiles(
            Path.Combine(Directory.GetCurrentDirectory(), "..", "..", "..", "..", "..",
                "src", "Cybersole.Stores", "Flows"), "*.cs");
        _out.WriteLine($"{flows.Length} flow files");

        foreach (var file in flows)
        {
            var text = File.ReadAllText(file);
            foreach (var banned in new[] { "/cart/change.js", "/cart/clear.js" })
            {
                var live = text.Split('\n')
                    .Where(l => l.Contains(banned, StringComparison.Ordinal)
                                && !l.TrimStart().StartsWith("//", StringComparison.Ordinal)
                                && !l.TrimStart().StartsWith("///", StringComparison.Ordinal))
                    .ToList();

                if (live.Count > 0)
                    _out.WriteLine($"{Path.GetFileName(file)}: {banned} x{live.Count}");

                Assert.Empty(live);
            }
        }
    }

    /// <summary>The two endpoints the image does have are the ones the flow uses.</summary>
    [Fact]
    public void TheFlowUsesAddAndUpdate()
    {
        var shopify = Source("ShopifyFlow.cs");

        Assert.Contains("/cart/add.js", shopify);
        Assert.Contains("/cart/update.js", shopify);

        _out.WriteLine("ShopifyFlow uses cart/add.js + cart/update.js");
    }
}
