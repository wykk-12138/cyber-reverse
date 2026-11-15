using Cybersole.Core.Models;
using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// TaskGroup.ShippingRate travelled nowhere. The field existed and said "Preferred shipping
/// method/price for this group", ShippingRatesCreatorView wrote it, and no code read it — the
/// same shape as the raised-but-unsubscribed events of round 180, one layer down.
///
/// The picker is what makes it mean something: given a Shopify shipping_rates body and the group's
/// preference, choose the rate. It is a pure function over a JSON string, so it can be tested
/// without a network or a UI — which is why the fix was worth making rather than only recording.
/// </summary>
public class ShippingRateSelectionTests
{
    private readonly ITestOutputHelper _out;
    public ShippingRateSelectionTests(ITestOutputHelper output) => _out = output;

    private const string Body = """
        {
          "shipping_rates": [
            { "name": "Standard Shipping", "handle": "h-standard", "price": "5.00" },
            { "name": "Express Shipping",  "handle": "h-express",  "price": "12.50" },
            { "name": "Overnight",         "handle": "h-night",    "price": "29.00" }
          ]
        }
        """;

    [Fact]
    public void AnExactNameSelectsThatRate()
    {
        var picked = ShopifyFlow.PickRate(Body, "Express Shipping");

        _out.WriteLine($"{picked?.Name} / {picked?.Handle} / {picked?.Price}");

        Assert.NotNull(picked);
        Assert.Equal("h-express", picked!.Value.Handle);
    }

    [Fact]
    public void APartialNameSelectsTheFirstMatch()
    {
        // a group may store "Overnight" or "overnight" or "night" — the field is free text
        foreach (var want in new[] { "Overnight", "overnight", "night", "NIGHT" })
        {
            var picked = ShopifyFlow.PickRate(Body, want);
            _out.WriteLine($"{want,-10} -> {picked?.Name ?? "(none)"}");
            Assert.NotNull(picked);
            Assert.Equal("h-night", picked!.Value.Handle);
        }
    }

    [Fact]
    public void APriceSelectsTheRateWithThatPrice()
    {
        var picked = ShopifyFlow.PickRate(Body, "12.50");

        _out.WriteLine($"{picked?.Name} / {picked?.Price}");

        Assert.NotNull(picked);
        Assert.Equal("h-express", picked!.Value.Handle);
    }

    [Fact]
    public void ABlankPreferenceSelectsNothing()
    {
        // the important case: a group that never set the field must behave exactly as before
        foreach (var blank in new[] { null, "", "   " })
        {
            var picked = ShopifyFlow.PickRate(Body, blank);
            _out.WriteLine($"{blank ?? "(null)"} -> {(picked is null ? "(none)" : picked.Value.Name)}");
            Assert.Null(picked);
        }
    }

    [Fact]
    public void AnUnknownPreferenceSelectsNothing()
    {
        var picked = ShopifyFlow.PickRate(Body, "Teleportation");

        _out.WriteLine($"Teleportation -> {(picked is null ? "(none)" : picked.Value.Name)}");

        Assert.Null(picked);
    }

    [Fact]
    public void AMalformedBodyDoesNotThrow()
    {
        foreach (var body in new[] { "", "{}", "not json", """{"shipping_rates": "nope"}""" })
        {
            var picked = ShopifyFlow.PickRate(body, "Express");
            _out.WriteLine($"{body,-28} -> {(picked is null ? "(none)" : picked.Value.Name)}");
            Assert.Null(picked);
        }
    }

    /// <summary>
    /// The field must have a reader now. This is the specific defect: the property existed, a
    /// view wrote it, and nothing consumed it.
    /// </summary>
    [Fact]
    public void TheShippingRateFieldHasAReader()
    {
        var root = new DirectoryInfo(AppContext.BaseDirectory);
        while (root is not null && !Directory.Exists(Path.Combine(root.FullName, "src")))
            root = root.Parent;
        Assert.NotNull(root);

        var files = Directory
            .EnumerateFiles(Path.Combine(root!.FullName, "src"), "*.cs", SearchOption.AllDirectories)
            .Where(f => !f.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}")
                        && !f.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}"))
            .ToList();

        var readers = files
            .Where(f => File.ReadAllText(f).Contains("group.ShippingRate", StringComparison.Ordinal)
                        || File.ReadAllText(f).Contains("?.ShippingRate", StringComparison.Ordinal))
            .Select(f => Path.GetFileName(f))
            .ToList();

        _out.WriteLine($"files reading ShippingRate: {string.Join(", ", readers)}");

        Assert.NotEmpty(readers);
    }
}
