using System.Linq;
using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Gateway selection, which is a filter over what a shop offers rather than a list of names.
///
/// <para>
/// R957. R956 corrected an invented session key but left a hard-coded array of four gateways, which was the same mistake
/// one layer down. Searching for how selection works found PreferredGateways and blockedGateways as settings,
/// RpcGetPaymentMethods to fetch what a shop offers, ParsePaymentMethods to read the answer, and IsWalletOnly to
/// classify one kind. So the set of gateways is whatever the shop returns, filtered by two settings -- not a constant.
/// </para>
/// </summary>
public class GatewaySelectionTests
{
    /// <summary>Preference order wins when the preferred one is offered and not blocked.</summary>
    [Fact]
    public void PreferenceOrderWins()
    {
        var chosen = StoreFlow.ChooseGateway(
            new[] { "stripe", "paypal", "klarna" },
            new[] { "paypal", "stripe" },
            Array.Empty<string>());

        Assert.Equal("paypal", chosen);
    }

    /// <summary>A blocked method never wins, even when it is the first preference.</summary>
    [Fact]
    public void BlockedAlwaysLoses()
    {
        var chosen = StoreFlow.ChooseGateway(
            new[] { "paypal", "stripe" },
            new[] { "paypal", "stripe" },
            new[] { "paypal" });

        Assert.Equal("stripe", chosen);
    }

    /// <summary>
    /// No preference means take the first unblocked offer rather than none: a shop that offers payment must not fail
    /// because nobody expressed a preference.
    /// </summary>
    [Fact]
    public void NoPreferenceTakesTheFirstUnblocked()
    {
        Assert.Equal("stripe", StoreFlow.ChooseGateway(new[] { "stripe", "paypal" }, Array.Empty<string>(), Array.Empty<string>()));
        Assert.Equal("paypal", StoreFlow.ChooseGateway(new[] { "stripe", "paypal" }, Array.Empty<string>(), new[] { "stripe" }));
    }

    /// <summary>Nothing offered, or everything blocked, means nothing chosen -- and that is null rather than a guess.</summary>
    [Fact]
    public void NoChoiceIsNull()
    {
        Assert.Null(StoreFlow.ChooseGateway(Array.Empty<string>(), new[] { "paypal" }, Array.Empty<string>()));
        Assert.Null(StoreFlow.ChooseGateway(null!, Array.Empty<string>(), Array.Empty<string>()));
        Assert.Null(StoreFlow.ChooseGateway(new[] { "paypal" }, Array.Empty<string>(), new[] { "paypal" }));
    }

    /// <summary>Comparison ignores case, because a shop's spelling and a setting's spelling need not agree.</summary>
    [Fact]
    public void ComparisonIgnoresCase()
    {
        Assert.Equal("PayPal", StoreFlow.ChooseGateway(new[] { "PayPal" }, new[] { "paypal" }, Array.Empty<string>()));
        Assert.Null(StoreFlow.ChooseGateway(new[] { "PayPal" }, Array.Empty<string>(), new[] { "PAYPAL" }));
    }

    /// <summary>Wallets are classified separately because they need no card, and the image has a name for it.</summary>
    [Theory]
    [InlineData("paypal", true)]
    [InlineData("apple_pay", true)]
    [InlineData("GooglePay", true)]
    [InlineData("some_wallet_method", true)]
    [InlineData("stripe", false)]
    [InlineData("klarna", false)]
    [InlineData(null, false)]
    public void WalletClassification(string? method, bool expected)
    {
        Assert.Equal(expected, StoreFlow.IsWalletOnly(method));
    }

    /// <summary>The two settings are named as the image spells them.</summary>
    [Fact]
    public void TheSettingsUseTheImagesSpellings()
    {
        Assert.Equal("PreferredGateways", StoreFlow.PreferredGatewaysSetting);
        Assert.Equal("blockedGateways", StoreFlow.BlockedGatewaysSetting);
    }

    /// <summary>
    /// The invented array is gone: the source must not carry a fixed gateway list any more.
    /// </summary>
    [Fact]
    public void TheFixedListIsGone()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));

        Assert.DoesNotContain("internal static readonly string[] PaymentGateways", doc);
        Assert.Contains("not a constant at all", doc);
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir != null && !System.IO.Directory.Exists(System.IO.Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }
}