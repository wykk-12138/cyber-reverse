using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Http.Stores;
using Cybersole.Stores.Abstractions;

namespace Cybersole.Stores.Modules;

/// <summary>Kith — Shopify Plus storefront with a custom theme; reuses the Shopify JSON contract.</summary>
public sealed class KithModule : StoreModuleBase
{
    private readonly ShopifyModule _shopify = new();

    public override string Id => "kith";
    public override string Name => "Kith";
    public override IReadOnlyList<string> Domains => new[] { "kith.com", "kithnyc.com" };

    public override Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
        => _shopify.MonitorAsync(ctx, ct);

    public override Task<CheckoutOutcome> CheckoutAsync(CheckoutContext ctx, CancellationToken ct)
        => _shopify.CheckoutAsync(ctx, ct);
}

/// <summary>Yeezy Supply — queue-guarded drops; monitor polls the product API, checkout posts to cart.</summary>
public sealed class YeezySupplyModule : StoreModuleBase
{
    public override string Id => "yeezysupply";
    public override string Name => "Yeezy Supply";
    public override IReadOnlyList<string> Domains => new[] { "yeezysupply.com", "adidas.com", "confirmed.com" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var origin = new Uri(ctx.Url);
            var api = $"{origin.Scheme}://{origin.Host}/api/products/{Uri.EscapeDataString(origin.AbsolutePath.Trim('/'))}";
            var res = await ctx.Http.GetAsync(api,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "yeezy-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
            {
                // fall back to the product page (queue/captcha walls are common)
                res = await ctx.Http.GetAsync(ctx.Url,
                    Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "yeezy-page"), ct).ConfigureAwait(false);
            }

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            if (res.Body.Contains("captcha", StringComparison.OrdinalIgnoreCase))
                return new MonitorResult { Status = MonitorStatus.Captcha, Raw = res.Body };

            var title = MatchGroup(res.Body, @"""name""\s*:\s*""([^""]{3,80})""");
            var price = MatchGroup(res.Body, @"""price""\s*:\s*([\d.]+)");
            var inStock = res.Body.Contains("\"inStock\":true", StringComparison.OrdinalIgnoreCase) ||
                          res.Body.Contains("\"available\":true", StringComparison.OrdinalIgnoreCase);

            return new MonitorResult
            {
                Status = inStock ? MonitorStatus.Available : MonitorStatus.SoldOut,
                ProductName = title,
                Price = price,
                Sizes = System.Text.RegularExpressions.Regex
                    .Matches(res.Body, @"""size""\s*:\s*""([^""]{1,6})""")
                    .Select(m => m.Groups[1].Value).Distinct().ToList(),
                Raw = res.Body,
            };
        }
        catch (Exception ex)
        {
            return MonitorResult.Fail(ex.Message);
        }
    }

    public override async Task<CheckoutOutcome> CheckoutAsync(CheckoutContext ctx, CancellationToken ct)
    {
        try
        {
            var origin = new Uri(ctx.Url);
            var add = await ctx.Http.PostJsonAsync($"{origin.Scheme}://{origin.Host}/api/cart",
                Newtonsoft.Json.JsonConvert.SerializeObject(new { sku = ctx.VariantId, size = ctx.Size, quantity = 1 }),
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "yeezy-cart"), ct).ConfigureAwait(false);

            var order = MatchGroup(add.Body, @"""orderNumber""\s*:\s*""?([\w\-]+)""?");
            return new CheckoutOutcome
            {
                Success = add.IsSuccess && order is not null,
                OrderNumber = order,
                Result = order is not null ? CheckoutResult.Success : CheckoutResult.Declined,
                Error = add.IsSuccess ? null : $"HTTP {add.StatusCode}",
            };
        }
        catch (Exception ex)
        {
            return new CheckoutOutcome { Success = false, Error = ex.Message, Result = CheckoutResult.Error };
        }
    }
}

/// <summary>Offspring / Office — UK retailers sharing a Magento-style cart API.</summary>
public sealed class OffspringModule : StoreModuleBase
{
    public override string Id => "offspring";
    public override string Name => "Offspring / Office";
    public override IReadOnlyList<string> Domains => new[] { "offspring.co.uk", "office.co.uk", "offspring.com" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "offspring-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            var jsonLd = MatchGroup(res.Body, @"<script[^>]*application/ld\+json[^>]*>(.*?)</script>", 1);
            var title = jsonLd is null ? MatchGroup(res.Body, @"<title>([^<|]+)") : MatchGroup(jsonLd, @"""name""\s*:\s*""([^""]+)""");
            var price = jsonLd is null ? MatchGroup(res.Body, @"£\s*([\d,]+\.\d{2})") : MatchGroup(jsonLd, @"""price""\s*:\s*""?([\d.]+)""?");
            var available = jsonLd?.Contains("\"availability\":\"http://schema.org/InStock\"", StringComparison.OrdinalIgnoreCase) ?? false;

            return new MonitorResult
            {
                Status = available ? MonitorStatus.Available : MonitorStatus.SoldOut,
                ProductName = title,
                Price = price,
                Sizes = System.Text.RegularExpressions.Regex
                    .Matches(res.Body, @"data-size=""([^""]+)""")
                    .Select(m => m.Groups[1].Value).Distinct().ToList(),
                Raw = res.Body,
            };
        }
        catch (Exception ex)
        {
            return MonitorResult.Fail(ex.Message);
        }
    }

    public override async Task<CheckoutOutcome> CheckoutAsync(CheckoutContext ctx, CancellationToken ct)
    {
        try
        {
            var origin = new Uri(ctx.Url);
            var add = await ctx.Http.PostFormAsync($"{origin.Scheme}://{origin.Host}/checkout/cart/add",
                new Dictionary<string, string>
                {
                    ["product"] = ctx.VariantId,
                    ["qty"] = "1",
                    ["size"] = ctx.Size,
                },
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "offspring-cart"), ct).ConfigureAwait(false);

            var order = MatchGroup(add.Body, @"""order(?:Id|Number)""\s*:\s*""?([\w\-]+)""?");
            return new CheckoutOutcome
            {
                Success = add.IsSuccess && order is not null,
                OrderNumber = order,
                Result = order is not null ? CheckoutResult.Success : CheckoutResult.Declined,
                Error = add.IsSuccess ? null : $"HTTP {add.StatusCode}",
            };
        }
        catch (Exception ex)
        {
            return new CheckoutOutcome { Success = false, Error = ex.Message, Result = CheckoutResult.Error };
        }
    }
}
