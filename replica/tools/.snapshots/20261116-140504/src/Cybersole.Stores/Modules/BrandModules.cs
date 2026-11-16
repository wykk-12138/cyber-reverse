using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Http.Stores;
using Cybersole.Stores.Abstractions;

namespace Cybersole.Stores.Modules;

/// <summary>Fanatics — licensed sports merchandise, JSON availability on PDP.</summary>
public sealed class FanaticsModule : StoreModuleBase
{
    public override string Id => "fanatics";
    public override string Name => "Fanatics";
    public override IReadOnlyList<string> Domains => new[] { "fanatics.com", "id.fanatics.com", "lids.com" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "fanatics-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            var title = MatchGroup(res.Body, @"<title>([^<|]+)");
            var price = MatchGroup(res.Body, @"""price""\s*:\s*""?([\d.]+)""?");
            var available = res.Body.Contains("\"availability\":\"InStock\"", StringComparison.OrdinalIgnoreCase) ||
                            res.Body.Contains("Add to Cart", StringComparison.OrdinalIgnoreCase);

            return new MonitorResult
            {
                Status = available ? MonitorStatus.Available : MonitorStatus.SoldOut,
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
            var add = await ctx.Http.PostJsonAsync($"{origin.Scheme}://{origin.Host}/api/cart/add",
                Newtonsoft.Json.JsonConvert.SerializeObject(new { sku = ctx.VariantId, quantity = 1 }),
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "fanatics-cart"), ct).ConfigureAwait(false);

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

/// <summary>Riot Games merch — SSO-gated storefront, cart via JSON API.</summary>
public sealed class RiotGamesModule : StoreModuleBase
{
    public override string Id => "riotgames";
    public override string Name => "Riot Games";
    public override IReadOnlyList<string> Domains => new[] { "merch.riotgames.com", "authenticate.riotgames.com" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "riot-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            var title = MatchGroup(res.Body, @"<title>([^<|]+)");
            var price = MatchGroup(res.Body, @"\$\s*([\d,]+\.\d{2})");
            var available = res.Body.Contains("\"inStock\":true", StringComparison.OrdinalIgnoreCase) ||
                            res.Body.Contains("Add to cart", StringComparison.OrdinalIgnoreCase);

            return new MonitorResult
            {
                Status = available ? MonitorStatus.Available : MonitorStatus.SoldOut,
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
            var add = await ctx.Http.PostJsonAsync($"{origin.Scheme}://{origin.Host}/cart/add.js",
                Newtonsoft.Json.JsonConvert.SerializeObject(new { id = ctx.VariantId, quantity = 1 }),
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "riot-cart"), ct).ConfigureAwait(false);

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

/// <summary>Hype Commerce — headless DTC platform used by several hype brands.</summary>
public sealed class HypeCommerceModule : StoreModuleBase
{
    public override string Id => "hypecommerce";
    public override string Name => "Hype Commerce";
    public override IReadOnlyList<string> Domains => new[] { "hypecommerce.io", "admin.hypecommerce.io" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "hype-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            var title = MatchGroup(res.Body, @"<title>([^<|]+)");
            var price = MatchGroup(res.Body, @"""price""\s*:\s*([\d.]+)");
            var available = res.Body.Contains("\"available\":true", StringComparison.OrdinalIgnoreCase);

            return new MonitorResult
            {
                Status = available ? MonitorStatus.Available : MonitorStatus.SoldOut,
                ProductName = title,
                Price = price,
                Sizes = System.Text.RegularExpressions.Regex
                    .Matches(res.Body, @"""size""\s*:\s*""([^""]+)""")
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
            var add = await ctx.Http.PostJsonAsync($"{origin.Scheme}://{origin.Host}/api/v1/cart",
                Newtonsoft.Json.JsonConvert.SerializeObject(new { variantId = ctx.VariantId, size = ctx.Size, quantity = 1 }),
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "hype-cart"), ct).ConfigureAwait(false);

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

/// <summary>Footpatrol — JD group UK retailer, queue guarded.</summary>
public sealed class FootpatrolModule : StoreModuleBase
{
    public override string Id => "footpatrol";
    public override string Name => "Footpatrol";
    public override IReadOnlyList<string> Domains => new[] { "footpatrol.com", "footpatrol.co.uk" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "footpatrol-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            if (res.Body.Contains("queue-it", StringComparison.OrdinalIgnoreCase))
                return new MonitorResult { Status = MonitorStatus.Unavailable, Raw = res.Body };

            var title = MatchGroup(res.Body, @"<title>([^<|]+)");
            var price = MatchGroup(res.Body, @"£\s*([\d,]+\.\d{2})");
            var available = res.Body.Contains("Add to bag", StringComparison.OrdinalIgnoreCase);

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
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "footpatrol-cart"), ct).ConfigureAwait(false);

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

/// <summary>Notre Shop — curated boutique, Shopify cart backend.</summary>
public sealed class NotreModule : StoreModuleBase
{
    public override string Id => "notre";
    public override string Name => "Notre";
    public override IReadOnlyList<string> Domains => new[] { "notre-shop.com", "notre.com" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "notre-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            var title = MatchGroup(res.Body, @"<title>([^<|]+)");
            var price = MatchGroup(res.Body, @"""price""\s*:\s*""?([\d.]+)""?");
            var available = res.Body.Contains("\"available\":true", StringComparison.OrdinalIgnoreCase) &&
                            !res.Body.Contains("\"available\":false", StringComparison.OrdinalIgnoreCase);

            return new MonitorResult
            {
                Status = available ? MonitorStatus.Available : MonitorStatus.SoldOut,
                ProductName = title,
                Price = price,
                Sizes = System.Text.RegularExpressions.Regex
                    .Matches(res.Body, @"""title""\s*:\s*""(\d+(?:\.\d+)?)""")
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
            var add = await ctx.Http.PostJsonAsync($"{origin.Scheme}://{origin.Host}/cart/add.js",
                Newtonsoft.Json.JsonConvert.SerializeObject(new { id = ctx.VariantId, quantity = 1 }),
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "notre-cart"), ct).ConfigureAwait(false);

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
