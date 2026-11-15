using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Http.Stores;
using Cybersole.Stores.Abstractions;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Modules;

/// <summary>
/// Shopify module — the highest-value integration of the original client.
/// Monitor uses the storefront <c>/products/{handle}.js</c> endpoint;
/// checkout uses the cart-permalink flow (fastest path, no browser).
/// </summary>
public sealed class ShopifyModule : StoreModuleBase
{
    private readonly string _id;
    private readonly string _name;
    private readonly IReadOnlyList<string> _domains;

    /// <summary>Default generic Shopify module (any *.myshopify.com / Shopify storefront).</summary>
    public ShopifyModule() : this("shopify", "Shopify", new[] { "myshopify.com", "shopify.com" })
    {
    }

    /// <summary>
    /// Store-specific Shopify module. Shopify powers hundreds of streetwear retailers, so instead of
    /// duplicating the whole monitor/checkout flow per brand, each brand is a thin alias.
    /// </summary>
    public ShopifyModule(string id, string name, IReadOnlyList<string> domains)
    {
        _id = id;
        _name = name;
        _domains = domains;
    }

    public override string Id => _id;
    public override string Name => _name;
    public override IReadOnlyList<string> Domains => _domains;

    /// <summary>
    /// Host match only. An earlier version also matched any "/products/" path, which made this
    /// module (registered first) swallow every brand alias — bodega.com resolved to "shopify".
    /// </summary>
    public override bool CanHandle(Uri url) => base.CanHandle(url);

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        var url = ctx.Url;
        if (string.IsNullOrWhiteSpace(url))
            return MonitorResult.Fail("empty url");

        // normalize: /products/{handle}?variant=... -> /products/{handle}.js
        var uri = new Uri(url);
        var handle = ExtractHandle(uri);
        if (handle is null)
            return MonitorResult.Fail("not a shopify product url");

        var jsUrl = $"{uri.Scheme}://{uri.Host}/products/{handle}.js";
        var opts = Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "shopify-monitor");

        NetResponse res;
        try
        {
            res = await ctx.Http.GetAsync(jsUrl, opts, ct).ConfigureAwait(false);
        }
        catch (Exception ex)
        {
            return MonitorResult.Fail(ex.Message);
        }

        if (res.StatusCode is 429 or 403)
            return new MonitorResult { Status = MonitorStatus.Captcha, Raw = res.Body };
        if (!res.IsSuccess)
            return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

        try
        {
            var json = JObject.Parse(res.Body);
            var title = json["title"]?.ToString();
            var image = (json["featured_image"] as JValue)?.Value?.ToString();
            var variants = json["variants"] as JArray ?? new JArray();

            var available = variants
                .Where(v => v["available"]?.ToObject<bool>() ?? false)
                .ToList();

            if (available.Count == 0)
                return new MonitorResult
                {
                    Status = MonitorStatus.SoldOut,
                    ProductName = title,
                    Image = image,
                };

            var first = available[0];
            var price = first["price"]?.ToObject<long>() is { } cents ? (cents / 100.0).ToString("0.00") : null;
            var sizes = available
                .Select(v => v["title"]?.ToString())
                .Where(s => !string.IsNullOrWhiteSpace(s))
                .Select(s => s!)
                .Distinct()
                .ToList();

            return new MonitorResult
            {
                Status = MonitorStatus.Available,
                ProductName = title,
                Image = image,
                Price = price,
                VariantId = first["id"]?.ToString(),
                VariantTitle = first["title"]?.ToString(),
                Sizes = sizes,
                Raw = res.Body,
            };
        }
        catch (Exception ex)
        {
            return MonitorResult.Fail($"parse error: {ex.Message}");
        }
    }

    public override async Task<CheckoutOutcome> CheckoutAsync(CheckoutContext ctx, CancellationToken ct)
    {
        try
        {
            // 1) add to cart
            var addUrl = $"{new Uri(ctx.Url).Scheme}://{new Uri(ctx.Url).Host}/cart/add.js";
            var payload = Newtonsoft.Json.JsonConvert.SerializeObject(new
            {
                id = long.TryParse(ctx.VariantId, out var vid) ? vid : 0,
                quantity = 1,
                properties = ctx.Extra,
            });

            var addRes = await ctx.Http.PostJsonAsync(addUrl, payload,
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "shopify-cart"), ct)
                .ConfigureAwait(false);

            if (!addRes.IsSuccess)
                return new CheckoutOutcome
                {
                    Success = false,
                    Error = $"cart/add.js HTTP {addRes.StatusCode}",
                    Result = CheckoutResult.Error,
                };

            // 2) cart permalink checkout
            var origin = new Uri(ctx.Url);
            var permalink = $"{origin.Scheme}://{origin.Host}/cart/{ctx.VariantId}:1";

            var checkoutRes = await ctx.Http.GetAsync(permalink,
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "shopify-checkout"), ct)
                .ConfigureAwait(false);

            var order = MatchGroup(checkoutRes.Body, @"order(?:s)?/(\d+)") ??
                        MatchGroup(checkoutRes.Body, @"""order_number""\s*:\s*""?(\d+)");

            var success = checkoutRes.IsSuccess &&
                          (order is not null ||
                           checkoutRes.Body.Contains("thank_you", StringComparison.OrdinalIgnoreCase));

            var form = CheckoutFormBuilder.Build(ctx.ProfileData, ctx.Account, ctx.Size);

            return new CheckoutOutcome
            {
                Success = success,
                OrderNumber = order,
                SubmittedFields = form,
                Price = MatchGroup(checkoutRes.Body, @"""total_price""\s*:\s*""?([\d.]+)"),
                Result = success ? CheckoutResult.Success : CheckoutResult.Declined,
                Details = { ["final_url"] = checkoutRes.Url.ToString() },
            };
        }
        catch (Exception ex)
        {
            return new CheckoutOutcome
            {
                Success = false,
                Error = ex.Message,
                Result = CheckoutResult.Error,
            };
        }
    }

    private static string? ExtractHandle(Uri uri)
    {
        var m = System.Text.RegularExpressions.Regex.Match(uri.AbsolutePath,
            @"/products/([^/?#]+)", System.Text.RegularExpressions.RegexOptions.IgnoreCase);
        return m.Success ? m.Groups[1].Value : null;
    }
}
