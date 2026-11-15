import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\ShopifyGraphQlTests.cs"
t = io.open(p, encoding="utf-8").read()

anchor = "    /// <summary><c>checkoutUrl</c> is found wherever the storefront nests it.</summary>"
add = '''    /// <summary>
    /// R98: the GraphQL read is wired into the flow, and the plain <c>/cart.js</c> read is still the
    /// fallback. A source-level check, because reaching either path needs a live storefront.
    ///
    /// <para>
    /// The interesting property is the <b>gate</b>: no storefront token means no GraphQL call. A
    /// storefront that does not offer a token is not an error, and the flow must not turn it into
    /// one — it just uses the endpoint it always used.
    /// </para>
    /// </summary>
    [Fact]
    public void TheFlowGatesGraphQlOnATokenAndFallsBackToCartJs()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;

        var source = File.ReadAllText(Path.Combine(dir!.FullName, "src", "Cybersole.Stores",
            "Flows", "ShopifyFlow.cs"));

        Assert.Contains("shopify.storefrontToken", source);
        Assert.Contains("shopify.cartId", source);
        Assert.Contains("GetCartViaGraphQlAsync", source);
        Assert.Contains("ShopifyGraphQl.CartQueryDocument", source);
        Assert.Contains("X-Shopify-Storefront-Access-Token", source);

        // the fallback is still there, and it is what runs when there is no token
        Assert.Contains("/cart.js", source);

        // GraphQL is inside an `if` on the token var, not unconditional
        var gate = source.IndexOf("TryGetValue(GraphQlTokenVar", StringComparison.Ordinal);
        var call = source.IndexOf("GetCartViaGraphQlAsync(c, token", StringComparison.Ordinal);
        _out.WriteLine($"gate at {gate}, call at {call}");

        Assert.True(gate > 0 && call > gate);
    }

'''

if anchor not in t:
    raise SystemExit("anchor missing")
if "TheFlowGatesGraphQlOnAToken" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("wiring test added")
