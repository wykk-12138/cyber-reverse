using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Http.Stores;
using Cybersole.Stores.Abstractions;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Modules;

/// <summary>
/// Nike SNKRS module — poll the product feed, resolve the SKU/variant,
/// then drive the checkout through the cart API.
/// </summary>
public sealed class NikeModule : StoreModuleBase
{
    public override string Id => "nike";
    public override string Name => "Nike";
    public override IReadOnlyList<string> Domains => new[] { "nike.com", "snkrs.nike.com" };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var styleColor = MatchGroup(ctx.Url, @"/([A-Z]{2}\d{4}-\d{3})", 1)
                             ?? MatchGroup(ctx.Url, @"styleColor=([A-Z0-9\-]+)", 1);
            if (string.IsNullOrEmpty(styleColor))
                return MonitorResult.Fail("nike: cannot resolve style color from url");

            var api = $"https://api.nike.com/product_feed/threads/v2/?filter=marketplace(US)&filter=language(en)" +
                      $"&filter=channelId(d9a5bc42-4b9c-4976-858a-f159cf99c647)&filter=productInfo.merchProduct.styleColor({styleColor})";

            var res = await ctx.Http.GetAsync(api,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "nike-thread"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            var root = JObject.Parse(res.Body);
            var objects = root["objects"] as JArray ?? new JArray();
            if (objects.Count == 0)
                return new MonitorResult { Status = MonitorStatus.Unavailable };

            var product = objects[0]?["productInfo"] as JArray;
            if (product is null)
                return new MonitorResult { Status = MonitorStatus.Unavailable };

            foreach (var info in product)
            {
                var status = info?["merchProduct"]?["status"]?.ToString();
                var price = info?["merchPrice"]?["currentPrice"]?.ToObject<decimal?>();
                var available = info?["availability"]?["available"]?.ToObject<bool?>() ?? false;
                var sizes = (info?["skus"] as JArray)?.Select(s => s?["countrySpecifications"]?.FirstOrDefault()?["localizedSize"]?.ToString())
                    .Where(s => !string.IsNullOrWhiteSpace(s)).Select(s => s!).Distinct().ToList() ?? new();

                if (status is "ACTIVE" && available)
                {
                    return new MonitorResult
                    {
                        Status = MonitorStatus.Available,
                        ProductName = info?["productContent"]?["fullTitle"]?.ToString(),
                        Price = price?.ToString("0.00"),
                        VariantId = info?["merchProduct"]?["id"]?.ToString(),
                        Sizes = sizes,
                        Raw = res.Body,
                    };
                }
            }

            return new MonitorResult { Status = MonitorStatus.SoldOut };
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
            var cartUrl = "https://api.nike.com/buy/carts/v2/US/Nike/SNKRS?format=simplified";
            var email = ctx.Extra.TryGetValue("email", out var e) ? e : null;
            var payload = Newtonsoft.Json.JsonConvert.SerializeObject(new
            {
                items = new[] { new { skuId = ctx.VariantId, quantity = 1 } },
                shippingAddress = email is null ? null : new { email },
            });

            var cart = await ctx.Http.PostJsonAsync(cartUrl, payload,
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "nike-cart"), ct)
                .ConfigureAwait(false);

            if (!cart.IsSuccess)
                return new CheckoutOutcome
                {
                    Success = false,
                    Error = $"cart HTTP {cart.StatusCode}",
                    Result = CheckoutResult.Error,
                };

            var cartId = JObject.Parse(cart.Body)["id"]?.ToString();
            var order = MatchGroup(cart.Body, @"""orderNumber""\s*:\s*""([^""]+)""");

            return new CheckoutOutcome
            {
                Success = order is not null,
                OrderNumber = order,
                Price = MatchGroup(cart.Body, @"""price""\s*:\s*([\d.]+)"),
                Result = order is not null ? CheckoutResult.Success : CheckoutResult.PaymentRequired,
                Details = { ["cart_id"] = cartId ?? string.Empty },
            };
        }
        catch (Exception ex)
        {
            return new CheckoutOutcome { Success = false, Error = ex.Message, Result = CheckoutResult.Error };
        }
    }
}

/// <summary>Footsites module — generic product-page scrape + add-to-cart POST.</summary>
public sealed class FootsitesModule : StoreModuleBase
{
    public override string Id => "footsites";
    public override string Name => "Footsites";
    public override IReadOnlyList<string> Domains => new[]
    {
        "footlocker.com", "champssports.com", "footaction.com", "kidsfootlocker.com", "eastbay.com",
    };

    public override async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
    {
        try
        {
            var res = await ctx.Http.GetAsync(ctx.Url,
                Options(ctx.Proxy, ctx.Profile, ctx.TimeoutSeconds, "footsites-monitor"), ct).ConfigureAwait(false);

            if (!res.IsSuccess)
                return new MonitorResult { Status = MonitorStatus.Blocked, Raw = res.Body };

            if (res.Body.Contains("Access Denied", StringComparison.OrdinalIgnoreCase))
                return new MonitorResult { Status = MonitorStatus.Captcha };

            var price = MatchGroup(res.Body, @"\$([\d,]+\.\d{2})");
            var title = MatchGroup(res.Body, @"<title>([^<]+)</title>");
            var sizes = System.Text.RegularExpressions.Regex
                .Matches(res.Body, @"""size""\s*:\s*""([^""]+)""")
                .Select(m => m.Groups[1].Value).Distinct().ToList();

            var inStock = res.Body.Contains("addToCart", StringComparison.OrdinalIgnoreCase) &&
                          !res.Body.Contains("soldOut", StringComparison.OrdinalIgnoreCase);

            return new MonitorResult
            {
                Status = inStock ? MonitorStatus.Available : MonitorStatus.SoldOut,
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
            var cartUrl = $"{origin.Scheme}://{origin.Host}/api/cart/add";
            var payload = Newtonsoft.Json.JsonConvert.SerializeObject(new
            {
                sku = ctx.VariantId,
                quantity = 1,
            });

            var res = await ctx.Http.PostJsonAsync(cartUrl, payload,
                Options(ctx.Proxy, ctx.BrowserProfile, ctx.TimeoutSeconds, "footsites-cart"), ct)
                .ConfigureAwait(false);

            var order = MatchGroup(res.Body, @"""order(?:Number|Id)""\s*:\s*""?([\w\-]+)""?");
            return new CheckoutOutcome
            {
                Success = res.IsSuccess && order is not null,
                OrderNumber = order,
                Error = res.IsSuccess ? null : $"HTTP {res.StatusCode}",
                Result = order is not null ? CheckoutResult.Success : CheckoutResult.Declined,
            };
        }
        catch (Exception ex)
        {
            return new CheckoutOutcome { Success = false, Error = ex.Message, Result = CheckoutResult.Error };
        }
    }
}
