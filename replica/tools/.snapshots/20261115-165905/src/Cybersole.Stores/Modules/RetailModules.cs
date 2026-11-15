using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Http.Stores;
using Cybersole.Stores.Abstractions;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Modules;

/// <summary>
/// End Clothing — JSON catalogue at api2.endclothing.com, product pages under /products/.
/// </summary>
public sealed class EndClothingModule : StoreModuleBase
{
    public override string Id => "endclothing";
    public override string Name => "END.";
    public override IReadOnlyList<string> Domains => new[] { "endclothing.com" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "end-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            if (res.Body.Contains("challenge-platform", StringComparison.OrdinalIgnoreCase))
                return new MonitorResult { Status = MonitorStatus.Captcha, Raw = res.Body };

            var title = MatchGroup(res.Body, @"<h1[^>]*class=""[^""]*product[^""]*""[^>]*>([^<]+)</h1>")
                        ?? MatchGroup(res.Body, @"<title>([^<|]+)");
            var price = MatchGroup(res.Body, @"""price""\s*:\s*""?([\d.]+)""?")
                        ?? MatchGroup(res.Body, @"£\s*([\d,]+\.\d{2})");
            var sizes = System.Text.RegularExpressions.Regex
                .Matches(res.Body, @"""size""\s*:\s*""([^""]+)""")
                .Select(m => m.Groups[1].Value).Distinct().ToList();
            var soldOut = res.Body.Contains("sold-out", StringComparison.OrdinalIgnoreCase) ||
                          res.Body.Contains("outOfStock", StringComparison.OrdinalIgnoreCase);

            return new MonitorResult
            {
                Status = soldOut ? MonitorStatus.SoldOut : MonitorStatus.Available,
                ProductName = title,
                Price = price,
                Sizes = sizes,
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
            var add = await ctx.Http.PostFormAsync($"{origin.Scheme}://{origin.Host}/cart/add",
                new Dictionary<string, string>
                {
                    ["productId"] = ctx.VariantId,
                    ["size"] = ctx.Size,
                    ["quantity"] = "1",
                },
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "end-cart"), ct).ConfigureAwait(false);

            var order = MatchGroup(add.Body, @"""order(?:Id|Number)""\s*:\s*""?([\w\-]+)""?");
            return new CheckoutOutcome
            {
                Success = add.IsSuccess && order is not null,
                OrderNumber = order,
                Error = add.IsSuccess ? null : $"HTTP {add.StatusCode}",
                Result = order is not null ? CheckoutResult.Success : CheckoutResult.Declined,
            };
        }
        catch (Exception ex)
        {
            return new CheckoutOutcome { Success = false, Error = ex.Message, Result = CheckoutResult.Error };
        }
    }
}

/// <summary>John Lewis — checkout page driven, session cookie + basket API.</summary>
public sealed class JohnLewisModule : StoreModuleBase
{
    public override string Id => "johnlewis";
    public override string Name => "John Lewis";
    public override IReadOnlyList<string> Domains => new[] { "johnlewis.com" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "jl-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            var title = MatchGroup(res.Body, @"""name""\s*:\s*""([^""]{3,80})""")
                        ?? MatchGroup(res.Body, @"<title>([^<|]+)");
            var price = MatchGroup(res.Body, @"""price""\s*:\s*\{[^}]*""amount""\s*:\s*([\d.]+)");
            var available = res.Body.Contains("\"inStock\":true", StringComparison.OrdinalIgnoreCase) ||
                            res.Body.Contains("Add to basket", StringComparison.OrdinalIgnoreCase);

            return new MonitorResult
            {
                Status = available ? MonitorStatus.Available : MonitorStatus.SoldOut,
                ProductName = title,
                Price = price,
                Sizes = System.Text.RegularExpressions.Regex
                    .Matches(res.Body, @"""size""\s*:\s*""([^”“]{1,10})""")
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
            var payload = Newtonsoft.Json.JsonConvert.SerializeObject(new
            {
                skuId = ctx.VariantId,
                quantity = 1,
                deliveryOption = "standard",
            });

            var add = await ctx.Http.PostJsonAsync($"{origin.Scheme}://{origin.Host}/api/basket/items", payload,
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "jl-basket"), ct).ConfigureAwait(false);

            if (!add.IsSuccess)
                return new CheckoutOutcome { Success = false, Error = $"basket HTTP {add.StatusCode}",
                    Result = CheckoutResult.Error };

            var checkout = await ctx.Http.GetAsync($"{origin.Scheme}://checkout.johnlewis.com/basket",
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "jl-checkout"), ct).ConfigureAwait(false);

            var order = MatchGroup(checkout.Body, @"""orderNumber""\s*:\s*""?([\w\-]+)""?");
            return new CheckoutOutcome
            {
                Success = order is not null,
                OrderNumber = order,
                Result = order is not null ? CheckoutResult.Success : CheckoutResult.PaymentRequired,
            };
        }
        catch (Exception ex)
        {
            return new CheckoutOutcome { Success = false, Error = ex.Message, Result = CheckoutResult.Error };
        }
    }
}

/// <summary>Pop Mart — blind-box drops, stock exposed through a product JSON endpoint.</summary>
public sealed class PopMartModule : StoreModuleBase
{
    public override string Id => "popmart";
    public override string Name => "Pop Mart";
    public override IReadOnlyList<string> Domains => new[] { "popmart.com" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "popmart-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            var json = TryParseJson(res.Body);
            if (json is not null)
            {
                var title = json["data"]?["product"]?["title"]?.ToString() ?? json["name"]?.ToString();
                var stock = json["data"]?["product"]?["stock"]?.ToObject<int?>() ?? 0;
                var price = json["data"]?["product"]?["price"]?.ToString();
                return new MonitorResult
                {
                    Status = stock > 0 ? MonitorStatus.Available : MonitorStatus.SoldOut,
                    ProductName = title,
                    Price = price,
                    Sizes = new List<string> { "One Size" },
                    Raw = res.Body,
                };
            }

            var soldOut = res.Body.Contains("sold out", StringComparison.OrdinalIgnoreCase);
            return new MonitorResult
            {
                Status = soldOut ? MonitorStatus.SoldOut : MonitorStatus.Available,
                ProductName = MatchGroup(res.Body, @"<title>([^<|]+)"),
                Price = MatchGroup(res.Body, @"\$([\d.]+)"),
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
            var add = await ctx.Http.PostJsonAsync($"{origin.Scheme}://{origin.Host}/api/cart/add",
                Newtonsoft.Json.JsonConvert.SerializeObject(new { skuId = ctx.VariantId, quantity = 1 }),
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "popmart-cart"), ct).ConfigureAwait(false);

            var order = MatchGroup(add.Body, @"""orderNumber""\s*:\s*""?([\w\-]+)""?");
            return new CheckoutOutcome
            {
                Success = add.IsSuccess && order is not null,
                OrderNumber = order,
                Error = add.IsSuccess ? null : $"HTTP {add.StatusCode}",
                Result = order is not null ? CheckoutResult.Success : CheckoutResult.Declined,
            };
        }
        catch (Exception ex)
        {
            return new CheckoutOutcome { Success = false, Error = ex.Message, Result = CheckoutResult.Error };
        }
    }

    private static JObject? TryParseJson(string body)
    {
        var trimmed = body.TrimStart();
        if (!trimmed.StartsWith('{')) return null;
        try { return JObject.Parse(trimmed); } catch { return null; }
    }
}
