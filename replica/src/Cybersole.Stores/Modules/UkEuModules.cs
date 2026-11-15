using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Http.Stores;
using Cybersole.Stores.Abstractions;

namespace Cybersole.Stores.Modules;

/// <summary>Sneakersnstuff — EU retailer, JSON product API + cart.</summary>
public sealed class SnsModule : StoreModuleBase
{
    public override string Id => "sns";
    public override string Name => "Sneakersnstuff";
    public override IReadOnlyList<string> Domains => new[] { "sneakersnstuff.com", "sns.se" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "sns-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            var json = res.Body.TrimStart();
            if (json.StartsWith('{'))
            {
                var o = Newtonsoft.Json.Linq.JObject.Parse(json);
                var variants = o["variants"] as Newtonsoft.Json.Linq.JArray;
                var available = variants?.Any(v => v?["available"]?.ToObject<bool>() ?? false) ?? false;
                var first = variants?.FirstOrDefault();
                return new MonitorResult
                {
                    Status = available ? MonitorStatus.Available : MonitorStatus.SoldOut,
                    ProductName = o["name"]?.ToString(),
                    Price = first?["price"]?.ToString(),
                    VariantId = first?["id"]?.ToString(),
                    Sizes = variants?.Select(v => v?["title"]?.ToString())
                        .Where(s => !string.IsNullOrWhiteSpace(s)).Select(s => s!).Distinct().ToList() ?? new(),
                    Raw = res.Body,
                };
            }

            var title = MatchGroup(res.Body, @"<title>([^<|]+)");
            var price = MatchGroup(res.Body, @"""price""\s*:\s*""?([\d.]+)""?");
            var inStock = res.Body.Contains("add-to-cart", StringComparison.OrdinalIgnoreCase);

            return new MonitorResult
            {
                Status = inStock ? MonitorStatus.Available : MonitorStatus.SoldOut,
                ProductName = title,
                Price = price,
                Sizes = new List<string> { "One Size" },
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
                new Dictionary<string, string> { ["id"] = ctx.VariantId, ["quantity"] = "1" },
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "sns-cart"), ct).ConfigureAwait(false);

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

/// <summary>Size? — UK retailer on a shared platform; product page + basket API.</summary>
public sealed class SizeModule : StoreModuleBase
{
    public override string Id => "size";
    public override string Name => "Size?";
    public override IReadOnlyList<string> Domains => new[] { "size.co.uk", "sizeofficial.co.uk" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "size-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            var title = MatchGroup(res.Body, @"<title>([^<|]+)");
            var price = MatchGroup(res.Body, @"£\s*([\d,]+\.\d{2})");
            var available = res.Body.Contains("\"availability\":\"http://schema.org/InStock\"", StringComparison.OrdinalIgnoreCase) ||
                            res.Body.Contains("Add to bag", StringComparison.OrdinalIgnoreCase);

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
                new Dictionary<string, string> { ["product"] = ctx.VariantId, ["qty"] = "1", ["size"] = ctx.Size },
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "size-cart"), ct).ConfigureAwait(false);

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

/// <summary>JD Sports — queue-guarded drops, basket API behind a token.</summary>
public sealed class JdSportsModule : StoreModuleBase
{
    public override string Id => "jdsports";
    public override string Name => "JD Sports";
    public override IReadOnlyList<string> Domains => new[] { "jdsports.co.uk", "jdsports.com", "jdsports.ie" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "jd-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            if (res.Body.Contains("queue-it", StringComparison.OrdinalIgnoreCase))
                return new MonitorResult { Status = MonitorStatus.Unavailable, Raw = res.Body };

            var title = MatchGroup(res.Body, @"<title>([^<|]+)");
            var price = MatchGroup(res.Body, @"£\s*([\d,]+\.\d{2})");
            var available = res.Body.Contains("\"inStock\":true", StringComparison.OrdinalIgnoreCase) ||
                            res.Body.Contains("Add to bag", StringComparison.OrdinalIgnoreCase);

            return new MonitorResult
            {
                Status = available ? MonitorStatus.Available : MonitorStatus.SoldOut,
                ProductName = title,
                Price = price,
                Sizes = System.Text.RegularExpressions.Regex
                    .Matches(res.Body, @"""sizeName""\s*:\s*""([^""]+)""")
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
            var add = await ctx.Http.PostJsonAsync($"{origin.Scheme}://{origin.Host}/api/basket/add",
                Newtonsoft.Json.JsonConvert.SerializeObject(new { sku = ctx.VariantId, quantity = 1 }),
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "jd-cart"), ct).ConfigureAwait(false);

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
