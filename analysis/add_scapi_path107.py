import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\DemandwareFlow.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.VariantId))
            return StepOutcome.Fail("demandware: no pid to add");

        var form = new Dictionary<string, string>
        {
            ["pid"] = c.Session.VariantId!,
            ["quantity"] = c.Session.Quantity.ToString(),
        };

        var res = await PostFormAsync(c, Controller(c, DemandwareControllers.CartAddProduct), form,
            Tag() + "-add", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("demandware add failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"demandware add HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }'''

new = '''    /// <summary>Session var holding an SCAPI OAuth bearer token, when the store runs headless.</summary>
    public const string ScapiTokenVar = "scapi.token";

    /// <summary>Session var holding the SCAPI basket id returned by <c>createBasket</c>.</summary>
    public const string ScapiBasketVar = "scapi.basketId";

    /// <summary>The SCAPI organisation id, which every basket call needs.</summary>
    public const string ScapiOrgVar = "scapi.organizationId";

    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.VariantId))
            return StepOutcome.Fail("demandware: no pid to add");

        // R107: the image drives SFCC two ways. When the store hands out an SCAPI token the basket
        // calls go through /scapi/ShopperBaskets/*; otherwise the classic demandware.store
        // controller is the path this flow always used. Both are real; a store runs one or the other.
        if (c.Session.Vars.TryGetValue(ScapiTokenVar, out var token) && !string.IsNullOrWhiteSpace(token))
        {
            var scapi = await AddToCartViaScapiAsync(c, token, ct).ConfigureAwait(false);
            if (scapi is not null) return scapi.Value;
        }

        var form = new Dictionary<string, string>
        {
            ["pid"] = c.Session.VariantId!,
            ["quantity"] = c.Session.Quantity.ToString(),
        };

        var res = await PostFormAsync(c, Controller(c, DemandwareControllers.CartAddProduct), form,
            Tag() + "-add", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("demandware add failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"demandware add HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// The SCAPI half of <see cref="AddToCartAsync"/>: create a basket if there is none, then add the
    /// item. Returns null on any failure so the caller falls back to the classic controller rather
    /// than reporting a checkout failure for a capability the store may not offer.
    /// </summary>
    private async Task<StepOutcome?> AddToCartViaScapiAsync(
        FlowContext c, string token, CancellationToken ct)
    {
        var origin = Origin(c.Url);
        c.Session.Headers["Authorization"] = "Bearer " + token;
        try
        {
            if (!c.Session.Vars.TryGetValue(ScapiBasketVar, out var basketId) || string.IsNullOrWhiteSpace(basketId))
            {
                var created = await PostJsonAsync(c, origin + ScapiEndpoints.CreateBasket, "{}",
                    Tag() + "-scapi-create", ct).ConfigureAwait(false);

                if (created is null || !created.IsSuccess) return null;

                basketId = JObject.Parse(created.Body)["basketId"]?.ToString();
                if (string.IsNullOrWhiteSpace(basketId)) return null;

                c.Session.Vars[ScapiBasketVar] = basketId!;
            }

            var org = c.Session.Vars.TryGetValue(ScapiOrgVar, out var organization) ? organization : string.Empty;

            var body = new JObject
            {
                ["productId"] = c.Session.VariantId,
                ["quantity"] = c.Session.Quantity,
            };

            var url = origin + ScapiEndpoints.AddItemToBasket + "?siteId=" + Uri.EscapeDataString(SiteId(c));

            var added = await PostJsonAsync(c, url, body.ToString(Newtonsoft.Json.Formatting.None),
                Tag() + "-scapi-add", ct).ConfigureAwait(false);

            if (added is null || !added.IsSuccess) return null;

            c.Session.Vars["cart"] = added.Body;
            if (!string.IsNullOrEmpty(org)) c.Session.Vars["scapi.org"] = org;
            return StepOutcome.Success();
        }
        finally
        {
            c.Session.Headers.Remove("Authorization");
        }
    }

    /// <summary>
    /// The <c>siteId</c> an SCAPI call needs. It is the site id the store already carries
    /// (<c>Sites-{site}-Site</c>), not a separate value.
    /// </summary>
    private static string SiteId(FlowContext c) =>
        c.Session.Vars.TryGetValue("site", out var site) && !string.IsNullOrWhiteSpace(site)
            ? site
            : "default";'''

if old not in t:
    raise SystemExit("AddToCartAsync anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("DemandwareFlow: SCAPI basket path added with a classic fallback")
