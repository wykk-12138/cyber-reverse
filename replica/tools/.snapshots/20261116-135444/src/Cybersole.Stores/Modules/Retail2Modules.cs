using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Http.Stores;
using Cybersole.Stores.Abstractions;

namespace Cybersole.Stores.Modules;

/// <summary>Casio — watch drops, product JSON exposed under /api/product.</summary>
public sealed class CasioModule : StoreModuleBase
{
    public override string Id => "casio";
    public override string Name => "Casio";
    public override IReadOnlyList<string> Domains => new[] { "casio.com", "casio.co.uk", "gshock.com" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "casio-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            var title = MatchGroup(res.Body, @"<title>([^<|]+)");
            var price = MatchGroup(res.Body, @"""price""\s*:\s*""?([\d.]+)""?")
                        ?? MatchGroup(res.Body, @"£\s*([\d,]+\.\d{2})");
            var addToCart = res.Body.Contains("add-to-cart", StringComparison.OrdinalIgnoreCase) &&
                            !res.Body.Contains("out-of-stock", StringComparison.OrdinalIgnoreCase);

            return new MonitorResult
            {
                Status = addToCart ? MonitorStatus.Available : MonitorStatus.SoldOut,
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
                new Dictionary<string, string>
                {
                    ["id"] = ctx.VariantId,
                    ["quantity"] = "1",
                },
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "casio-cart"), ct).ConfigureAwait(false);

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

/// <summary>Warhammer — preorder windows, B2C auth + basket API.</summary>
public sealed class WarhammerModule : StoreModuleBase
{
    public override string Id => "warhammer";
    public override string Name => "Warhammer";
    public override IReadOnlyList<string> Domains => new[] { "warhammer.com", "mywarhammer.com", "games-workshop.com" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "warhammer-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            var title = MatchGroup(res.Body, @"<title>([^<|]+)");
            var price = MatchGroup(res.Body, @"""price""\s*:\s*\{[^}]*""value""\s*:\s*([\d.]+)");
            var inStock = res.Body.Contains("\"inStock\":true", StringComparison.OrdinalIgnoreCase) ||
                          res.Body.Contains("Add to basket", StringComparison.OrdinalIgnoreCase);

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
            var add = await ctx.Http.PostJsonAsync($"{origin.Scheme}://{origin.Host}/api/basket/add",
                Newtonsoft.Json.JsonConvert.SerializeObject(new { sku = ctx.VariantId, quantity = 1 }),
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "warhammer-basket"), ct).ConfigureAwait(false);

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

/// <summary>JB Hi-Fi — AU retailer, Azure AD B2C auth + basket.</summary>
public sealed class JbHiFiModule : StoreModuleBase
{
    public override string Id => "jbhifi";
    public override string Name => "JB Hi-Fi";
    public override IReadOnlyList<string> Domains => new[] { "jbhifi.com.au" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "jbhifi-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            var title = MatchGroup(res.Body, @"<title>([^<|]+)");
            var price = MatchGroup(res.Body, @"""price""\s*:\s*([\d.]+)");
            var available = res.Body.Contains("\"available\":true", StringComparison.OrdinalIgnoreCase) ||
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
            var add = await ctx.Http.PostJsonAsync($"{origin.Scheme}://{origin.Host}/api/cart/add",
                Newtonsoft.Json.JsonConvert.SerializeObject(new { skuId = ctx.VariantId, quantity = 1 }),
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "jbhifi-cart"), ct).ConfigureAwait(false);

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

/// <summary>Superswipe — entry-gated drops with turnstile + country data.</summary>
public sealed class SuperswipeModule : StoreModuleBase
{
    public override string Id => "superswipe";
    public override string Name => "Superswipe";
    public override IReadOnlyList<string> Domains => new[] { "superswipe.com" };

    public override CaptchaChallenge? CreateChallenge(string pageUrl, string? siteKey = null, string kind = "turnstile")
        => base.CreateChallenge(pageUrl, siteKey, "turnstile");

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "superswipe-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            if (res.Body.Contains("turnstile", StringComparison.OrdinalIgnoreCase))
                return new MonitorResult { Status = MonitorStatus.Captcha, Raw = res.Body };

            var open = res.Body.Contains("\"open\":true", StringComparison.OrdinalIgnoreCase) ||
                       res.Body.Contains("Enter", StringComparison.OrdinalIgnoreCase);

            return new MonitorResult
            {
                Status = open ? MonitorStatus.Available : MonitorStatus.Unavailable,
                ProductName = MatchGroup(res.Body, @"<title>([^<|]+)"),
                Price = "0.00",
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
            var payload = Newtonsoft.Json.JsonConvert.SerializeObject(new
            {
                email = ctx.ProfileData.Email,
                name = $"{ctx.ProfileData.FirstName} {ctx.ProfileData.LastName}".Trim(),
                country = ctx.ProfileData.Country,
                turnstileToken = ctx.Extra.GetValueOrDefault("turnstile"),
            });
            var res = await ctx.Http.PostJsonAsync($"{origin.Scheme}://{origin.Host}/api/enter", payload,
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "superswipe-enter"), ct).ConfigureAwait(false);

            if (res.Body.Contains("turnstile", StringComparison.OrdinalIgnoreCase))
                return new CheckoutOutcome { Success = false, Result = CheckoutResult.Declined, Error = "captcha required" };

            var conf = MatchGroup(res.Body, @"""entryId""\s*:\s*""?([\w\-]+)""?");
            return new CheckoutOutcome
            {
                Success = res.IsSuccess && conf is not null,
                OrderNumber = conf,
                Result = conf is not null ? CheckoutResult.Success : CheckoutResult.Declined,
            };
        }
        catch (Exception ex)
        {
            return new CheckoutOutcome { Success = false, Error = ex.Message, Result = CheckoutResult.Error };
        }
    }
}

/// <summary>Pocket Games — NL retailer with a JSON catalog API.</summary>
public sealed class PocketGamesModule : StoreModuleBase
{
    public override string Id => "pocketgames";
    public override string Name => "Pocket Games";
    public override IReadOnlyList<string> Domains => new[] { "pocketgames.nl", "pocketgames.com" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "pocketgames-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            var title = MatchGroup(res.Body, @"<title>([^<|]+)");
            var price = MatchGroup(res.Body, @"""price""\s*:\s*""?([\d.,]+)""?");
            var available = res.Body.Contains("\"is_in_stock\":true", StringComparison.OrdinalIgnoreCase) ||
                            res.Body.Contains("add-to-cart", StringComparison.OrdinalIgnoreCase);

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
            var add = await ctx.Http.PostFormAsync($"{origin.Scheme}://{origin.Host}/checkout/cart/add",
                new Dictionary<string, string>
                {
                    ["product"] = ctx.VariantId,
                    ["qty"] = "1",
                },
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "pocketgames-cart"), ct).ConfigureAwait(false);

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
