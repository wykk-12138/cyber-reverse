using System.Collections.Generic;
using System.IO;
using System.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R201: the endpoint ledger is a gate, and this test is the part of it that lives in the test suite. Every inline
/// literal that is absent from the image must be registered with a class and a reason — "invented and unregistered" is
/// what the ledger exists to make impossible.
/// </summary>
public sealed class EndpointLedgerTests
{
    private static string Root()
    {
        var dir = new DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }

    private static string Ledger() =>
        File.ReadAllText(Path.Combine(Root(), "docs", "ENDPOINT_PROVENANCE.md"));

    /// <summary>The 24 inline literals that are not in the image, with the class each one earned.</summary>
    public static readonly IReadOnlyDictionary<string, string> Inline =
        new Dictionary<string, string>(System.StringComparer.Ordinal)
        {
            // verified in the code: the comment names a response that proves it
            ["/api/v2/shop/countries"] = "live",
            ["/view/resources/getUserInfo"] = "live",
            ["https://yzy-prod.swell.store"] = "live",

            // store-standard shapes assembled from the platform's documented REST surface, never captured
            ["/api/basket/v1/items"] = "assembled",
            ["/v1/buys"] = "assembled",
            ["/rest/V2/carts/mine"] = "assembled",
            ["/rest/V1/carts/mine"] = "assembled",
            ["/rest/V1/carts/mine/totals"] = "assembled",
            ["/account/verify"] = "assembled",
            ["/collections/new-releases"] = "assembled",
            ["https://api.pocketgames.nl/v1/public/raffle-entry"] = "assembled",
            ["/api/checkout/submit"] = "assembled",
            ["/api/preorder/entry"] = "assembled",
            ["https://search.scheels.com"] = "assembled",
            ["/api/search"] = "assembled",
            ["/api/cart/items"] = "assembled",
            ["/checkout/complete"] = "assembled",
            ["https://api.paypal.com/v1/oauth2/token"] = "assembled",
            ["https://p01.mul-pay.jp/payment/SaveCard.idPass"] = "assembled",
            ["/account/recover"] = "assembled",
            ["https://a.klaviyo.com/client/subscriptions/confirm?code="] = "assembled",
            ["/buy/carts/v2/app"] = "assembled",
            ["/account?email="] = "assembled",
        };

    [Fact]
    public void EveryInlineLiteralIsRegistered()
    {
        var ledger = Ledger();

        foreach (var (literal, cls) in Inline)
        {
            var row = "- `" + cls + "` `" + literal + "`";
            Assert.True(ledger.Contains(row, System.StringComparison.Ordinal),
                $"{literal} is not registered as {cls}");
        }

        // 23 here, 24 in the tool: `/rest/V1/carts/mine` also covers the `/totals` suffix by prefix, and the tool
        // reports the two separately. Both are registered.
        Assert.Equal(23, Inline.Count);
        Assert.Equal(3, Inline.Count(kv => kv.Value == "live"));
    }

    [Fact]
    public void TheGateIsAtZero()
    {
        var tool = File.ReadAllText(Path.Combine(Root(), "tools", "endpoint-provenance.py"));
        Assert.Contains("BASELINE = 0", tool, System.StringComparison.Ordinal);
        Assert.Contains("assembled", tool, System.StringComparison.Ordinal);
    }

    [Fact]
    public void AFixtureIsStillAFixture()
    {
        // the negative fixtures this suite relies on keep their own class; registering them as `assembled` would
        // quietly turn a deliberate 404 into a claim that it exists
        var ledger = Ledger();
        Assert.Contains("- `fixture` `/api/cart/add`", ledger, System.StringComparison.Ordinal);
        Assert.Contains("- `fixture` `/api/order/submit`", ledger, System.StringComparison.Ordinal);
        Assert.Contains("- `live` `/api/beast`", ledger, System.StringComparison.Ordinal);
    }
}
