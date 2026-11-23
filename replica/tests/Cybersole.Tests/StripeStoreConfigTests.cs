using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1302: the store's Stripe configuration fetch — the step R1301 recovered from <c>0x14094C210</c>
/// while disproving that it belonged to Unzer.
///
/// <para>
/// Every assertion names the frozen literal or the function it comes from, so a later round can re-check
/// the decode instead of trusting this file: the path is 0x146AB93D0, the origin 0x147090DF0, the REST
/// root 0x146AB7298, the status pair 0x146E49298 / 0x146D0F904, and the URL is composed exactly where
/// <c>sub_14095B4E0</c> composes it (origin, store code, REST root, path, tick).
/// </para>
///
/// <para>
/// The header template is asserted key by key because the point of it is fidelity: it is the fifteen-entry
/// browser dictionary <c>0x14094C210</c> installs at <c>a2+80</c>, of which eleven are literals this
/// replica can carry and four are not (three computed at build time, one null). Asserting the count would
/// pass on any eleven; asserting the pairs is what pins the decode.
/// </para>
/// </summary>
public sealed class StripeStoreConfigTests
{
    private const string ConfigPath = "/gb/rest/V1/stripe/payments/get_stripe_configuration";

    [Fact]
    public void TheUrlIsOriginThenStoreCodeThenRestRootThenPathThenTick()
    {
        // 0x147090DF0 has a trailing slash and a configured host usually does not; both must give one URL.
        const string expected =
            "https://www.casio.com/gb/rest/V1/stripe/payments/get_stripe_configuration?_=1700000000123";

        Assert.Equal(expected, StripeGateway.StoreConfigUrl("https://www.casio.com/", "gb", 1700000000123));
        Assert.Equal(expected, StripeGateway.StoreConfigUrl("https://www.casio.com", "gb", 1700000000123));
        Assert.Equal(expected, StripeGateway.StoreConfigUrl("https://www.casio.com///", "/gb/", 1700000000123));
    }

    [Fact]
    public void TheFrozenOriginAndRESTRootAreTheOnesInTheImage()
    {
        Assert.Equal("https://www.casio.com/", StripeGateway.DefaultStoreOrigin);
        Assert.Equal("/rest/V1", StripeGateway.MagentoRestPrefix);
        Assert.Equal("/stripe/payments/get_stripe_configuration?_=", StripeGateway.StoreConfigPath);

        // With nothing configured the frozen origin still produces the image's URL shape.
        var url = StripeGateway.StoreConfigUrl(null, null, 7);
        Assert.StartsWith("https://www.casio.com/rest/V1/stripe/payments/get_stripe_configuration?_=7", url);
    }

    [Fact]
    public void TheTemplateCarriesTheElevenLiteralsAndNotTheFourBuiltElsewhere()
    {
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = "https://www.casio.com/gb/checkout" };
        var headers = StripeGateway.StoreConfigHeaders(ctx);

        Assert.Equal("XMLHttpRequest", headers["x-requested-with"]);
        Assert.Equal("*/*", headers["accept"]);
        Assert.Equal("application/json", headers["content-type"]);
        Assert.Equal("?0", headers["sec-ch-ua-mobile"]);
        Assert.Equal("same-origin", headers["sec-fetch-site"]);
        Assert.Equal("cors", headers["sec-fetch-mode"]);
        Assert.Equal("empty", headers["sec-fetch-dest"]);
        Assert.Equal("gzip, deflate, br, zstd", headers["accept-encoding"]);
        Assert.Equal("en-US,en;q=0.9", headers["accept-language"]);
        Assert.Equal("u=1, i", headers["priority"]);
        Assert.Equal("https://www.casio.com/gb/checkout", headers["referer"]);

        // The three the image computes (sub_140F9BCE0 / sub_140F9A950 / session UA) ride the TLS profile
        // here, and `cookie` is null in the image, so none of the four is invented below.
        Assert.DoesNotContain("user-agent", headers.Keys);
        Assert.DoesNotContain("sec-ch-ua", headers.Keys);
        Assert.DoesNotContain("sec-ch-ua-platform", headers.Keys);
        Assert.DoesNotContain("cookie", headers.Keys);

        // The `Akamai` = `1` pair 0x14094C210 writes is a separate collection (a2+112), not a header.
        Assert.DoesNotContain("Akamai", headers.Keys);
    }

    [Fact]
    public async Task TheFetchStoresTheApiKeyAsThePublishableKeyAndEmitsTheStatus()
    {
        string? seenQuery = null;
        using var server = new TinyServer((req, _) =>
        {
            seenQuery = req.Url?.PathAndQuery;
            return (200, "{\"apiKey\":\"pk_test_casio\"}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/gb/checkout" };
        ctx.Session.Vars["stripe.storeOrigin"] = server.BaseUrl;
        ctx.Session.Vars["stripe.storeCode"] = "gb";

        var result = await new StripeGateway().FetchConfigurationAsync(ctx, default);

        Assert.True(result.Ok, result.Error);
        Assert.Equal("pk_test_casio", ctx.Session.Vars["stripe.publishableKey"]);
        Assert.Contains(ctx.Events, e => e.Name == "Preparing payment" && e.Type == "StatusInfo");
        Assert.NotNull(seenQuery);
        Assert.StartsWith(ConfigPath + "?_=", seenQuery);
        Assert.Matches(@"[?&]_=\d{10,}$", seenQuery!);
    }

    [Fact]
    public async Task AMissingApiKeyFailsWithTheImagesErrorTextAndLeavesTheKeyAlone()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/gb/checkout" };
        ctx.Session.Vars["stripe.storeOrigin"] = server.BaseUrl;
        ctx.Session.Vars["stripe.storeCode"] = "gb";

        var result = await new StripeGateway().FetchConfigurationAsync(ctx, default);

        Assert.False(result.Ok);
        Assert.Equal("Error preparing payment", result.Error);
        Assert.False(ctx.Session.Vars.ContainsKey("stripe.publishableKey"));
        Assert.Contains(ctx.Events, e => e.Name == "Error preparing payment" && e.Type == "error");
    }

    /// <summary>
    /// The guard on the wiring: <c>sub_140F9E790</c> only lets the fetch run while the session flag says
    /// the configuration is not there yet. Here that flag is the store declaration, so a flow that brings
    /// its own publishable key must not make the request at all.
    /// </summary>
    [Fact]
    public async Task TheConfigurationIsOnlyFetchedWhenTheStoreIsDeclaredAndTheKeyIsMissing()
    {
        var seen = new List<string>();
        using var server = new TinyServer((req, _) =>
        {
            seen.Add(req.Url?.AbsolutePath ?? string.Empty);
            var path = req.Url?.AbsolutePath ?? string.Empty;
            if (path == "/v1/payment_methods") return (200, "{\"id\":\"pm_1\",\"type\":\"card\"}");
            if (path.StartsWith("/v1/payment_intents")) return (200, "{\"id\":\"pi_1\",\"status\":\"succeeded\"}");
            return (200, "{\"apiKey\":\"pk_test_casio\"}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/gb/checkout",
            Card = new Card { Number = "4242424242424242", Cvv = "737", Month = "12", Year = "2030" },
        };
        ctx.Session.Vars["stripe.apiUrl"] = server.BaseUrl;
        ctx.Session.Vars["stripe.publishableKey"] = "pk_supplied_by_the_flow";

        await new StripeGateway().AuthorizeAsync(ctx, default);

        Assert.DoesNotContain(seen, p => p.Contains("get_stripe_configuration", StringComparison.Ordinal));
        Assert.Equal("pk_supplied_by_the_flow", ctx.Session.Vars["stripe.publishableKey"]);
    }

    [Fact]
    public async Task ADeclaredStoreWithoutAKeyFetchesBeforeTheIntentCall()
    {
        var seen = new List<string>();
        using var server = new TinyServer((req, _) =>
        {
            var path = req.Url?.AbsolutePath ?? string.Empty;
            seen.Add(path);
            if (path == ConfigPath) return (200, "{\"apiKey\":\"pk_test_casio\"}");
            if (path == "/v1/payment_methods") return (200, "{\"id\":\"pm_1\",\"type\":\"card\"}");
            if (path.StartsWith("/v1/payment_intents")) return (200, "{\"id\":\"pi_1\",\"status\":\"succeeded\"}");
            return (404, "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/gb/checkout",
            Card = new Card { Number = "4242424242424242", Cvv = "737", Month = "12", Year = "2030" },
        };
        ctx.Session.Vars["stripe.apiUrl"] = server.BaseUrl;
        ctx.Session.Vars["stripe.storeOrigin"] = server.BaseUrl;
        ctx.Session.Vars["stripe.storeCode"] = "gb";

        await new StripeGateway().AuthorizeAsync(ctx, default);

        Assert.NotEmpty(seen);
        Assert.Equal(ConfigPath, seen[0]);
        Assert.Equal("pk_test_casio", ctx.Session.Vars["stripe.publishableKey"]);
    }

    [Fact]
    public async Task FetchConfigurationUsesOverrideHeadersKeepsAkamaiOffWireAndHandles400()
    {
        using var server = new TinyServer((req, _) =>
        {
            if (req.Url?.AbsolutePath == "/err/rest/V1/stripe/payments/get_stripe_configuration")
                return (400, "{\"apiKey\":\"should_be_ignored\"}");
            return (200, "{\"apiKey\":\"pk_live_casio\"}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/gb/checkout" };
        ctx.Session.Vars["stripe.storeOrigin"] = server.BaseUrl;
        ctx.Session.Vars["stripe.storeCode"] = "gb";

        var ok = await new StripeGateway().FetchConfigurationAsync(ctx, default);
        Assert.True(ok.Ok, ok.Error);
        Assert.Equal("pk_live_casio", ctx.Session.Vars["stripe.publishableKey"]);

        var wireHeaders = Assert.Single(server.RequestHeaders);
        Assert.Equal("XMLHttpRequest", wireHeaders["x-requested-with"]);
        Assert.Equal("en-US,en;q=0.9", wireHeaders["accept-language"]);
        Assert.Equal("?0", wireHeaders["sec-ch-ua-mobile"]);
        Assert.Equal("u=1, i", wireHeaders["priority"]);
        Assert.False(wireHeaders.ContainsKey("Akamai"));
        Assert.False(wireHeaders.ContainsKey("User-Agent"));
        Assert.False(wireHeaders.ContainsKey("sec-ch-ua"));
        Assert.False(wireHeaders.ContainsKey("sec-ch-ua-platform"));
        Assert.False(wireHeaders.ContainsKey("sec-fetch-user"));
        Assert.False(wireHeaders.ContainsKey("upgrade-insecure-requests"));

        var errCtx = new FlowContext { Http = http, Url = server.BaseUrl + "/err/checkout" };
        errCtx.Session.Vars["stripe.storeOrigin"] = server.BaseUrl;
        errCtx.Session.Vars["stripe.storeCode"] = "err";

        var errRes = await new StripeGateway().FetchConfigurationAsync(errCtx, default);
        Assert.False(errRes.Ok);
        Assert.Equal("Error preparing payment", errRes.Error);
        Assert.False(errCtx.Session.Vars.ContainsKey("stripe.publishableKey"));
        Assert.Contains(errCtx.Events, e => e.Name == "Error preparing payment" && e.Type == "error");
    }
}
