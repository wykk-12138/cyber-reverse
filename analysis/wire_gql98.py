import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\ShopifyFlow.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetAsync(c, Origin(c.Url) + "/cart.js", "shopify-cart-get", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("shopify cart fetch failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"shopify cart HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        var total = JObject.Parse(res.Body)["total_price"]?.ToString();
        if (total is not null) c.Session.Vars["total"] = total;
        return StepOutcome.Success();
    }'''

new = '''    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)
    {
        // R98: the image carries a Storefront GraphQL cart read (a 354-character selection set with
        // checkoutUrl, totals and up to 250 lines) as well as the plain /cart.js read. A storefront
        // hands out a token to a headless store; without one there is nothing to query, so the
        // fallback is the path this flow already used.
        if (c.Session.Vars.TryGetValue(GraphQlTokenVar, out var token) && !string.IsNullOrWhiteSpace(token)
            && c.Session.Vars.TryGetValue(GraphQlCartVar, out var cartId) && !string.IsNullOrWhiteSpace(cartId))
        {
            var graph = await GetCartViaGraphQlAsync(c, token, cartId, ct).ConfigureAwait(false);
            if (graph is not null) return graph;
        }

        var res = await GetAsync(c, Origin(c.Url) + "/cart.js", "shopify-cart-get", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("shopify cart fetch failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"shopify cart HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        var total = JObject.Parse(res.Body)["total_price"]?.ToString();
        if (total is not null) c.Session.Vars["total"] = total;
        return StepOutcome.Success();
    }

    /// <summary>Session var holding a Storefront access token, when the store hands one out.</summary>
    public const string GraphQlTokenVar = "shopify.storefrontToken";

    /// <summary>Session var holding the GraphQL cart id (<c>gid://shopify/Cart/…</c>).</summary>
    public const string GraphQlCartVar = "shopify.cartId";

    /// <summary>
    /// Reads the cart through the Storefront GraphQL endpoint using the image's own selection set.
    /// Returns null when the call fails, so the caller falls back to <c>/cart.js</c> rather than
    /// reporting a checkout failure for a capability the store may simply not offer.
    /// </summary>
    private async Task<StepOutcome?> GetCartViaGraphQlAsync(
        FlowContext c, string token, string cartId, CancellationToken ct)
    {
        var document = ShopifyGraphQl.CartQueryDocument(
            "query Cart($cartId: ID!) { cart(id: $cartId) ");

        var payload = new JObject
        {
            ["query"] = document,
            ["variables"] = new JObject { ["cartId"] = cartId },
        };

        var url = ShopifyGraphQl.Endpoint(new Uri(c.Url).Host,
            c.Session.Vars.TryGetValue("shopify.apiVersion", out var version) && !string.IsNullOrWhiteSpace(version)
                ? version
                : "2025-04");

        c.Session.Headers["X-Shopify-Storefront-Access-Token"] = token;

        var res = await PostJsonAsync(c, url, payload.ToString(Newtonsoft.Json.Formatting.None),
            "shopify-cart-graphql", ct).ConfigureAwait(false);

        if (res is null || !res.IsSuccess) return null;

        var checkoutUrl = ShopifyGraphQl.ParseCheckoutUrl(res.Body);
        if (checkoutUrl is not null) c.Session.Vars["checkoutUrl"] = checkoutUrl;

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }'''

if old not in t:
    raise SystemExit("GetCartAsync anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("ShopifyFlow: GraphQL cart read wired with a /cart.js fallback")
