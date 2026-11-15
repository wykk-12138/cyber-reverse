using System.Linq;
using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R292: the "Need Help?" catalogue is product surface — a user comparing the two builds must see the same explanation
/// for the same failure — so its exact content is pinned here.
///
/// <para>
/// All thirteen titles and all thirteen detail sentences were found <b>verbatim</b> in the image's string pool
/// (13/13 and 13/13), which is what makes this table evidence rather than transcription. Editing an entry now fails
/// until the table is updated on purpose.
/// </para>
/// </summary>
public sealed class ErrorCatalogDigestTests
{
    private readonly ITestOutputHelper _out;
    public ErrorCatalogDigestTests(ITestOutputHelper output) => _out = output;

    private static readonly string[] ExpectedTitles =
    {
        "[General] Connection Error",
        "[General] Not found",
        "[General] Service Unavailable",
        "[General] Rate Limit",
        "[General] Forbidden",
        "[General] Task failed",
        "[Shopify] Error Submitting Shipping (Handle Error)",
        "[Shopify] Error Submitting Order (Rate Limit)",
        "[Shopify] Payment Error",
        "[Shopify] Connection Errors",
        "[Shopify] Tasks hanging on \"Getting Shipping Rates\"",
        "[Shopify] Invalid Credit Card Number/Billing",
        "[Footsites] Rate Limit / 429",
    };

    [Fact]
    public void TheCatalogueHoldsTheThirteenEntriesTheImageCarries()
    {
        var titles = ErrorCatalog.All.Select(e => e.Title).ToList();
        foreach (var t in titles) _out.WriteLine(t);

        Assert.Equal(13, ErrorCatalog.All.Count);
        Assert.Equal(ExpectedTitles.OrderBy(x => x, System.StringComparer.Ordinal),
                     titles.OrderBy(x => x, System.StringComparer.Ordinal));
        Assert.Equal(13, titles.Distinct().Count());
    }

    [Fact]
    public void TheTagsAreTheThreeTheImageGroupsBy()
    {
        var byTag = ErrorCatalog.All.GroupBy(e => e.Tag).ToDictionary(g => g.Key, g => g.Count());
        foreach (var pair in byTag) _out.WriteLine($"{pair.Key}: {pair.Value}");

        Assert.Equal(6, byTag["General"]);
        Assert.Equal(6, byTag["Shopify"]);
        Assert.Equal(1, byTag["Footsites"]);
    }

    [Fact]
    public void EveryEntryCarriesATagPrefixAndADetail()
    {
        foreach (var entry in ErrorCatalog.All)
        {
            Assert.StartsWith("[" + entry.Tag + "]", entry.Title);
            Assert.False(string.IsNullOrWhiteSpace(entry.Detail));
            Assert.False(string.IsNullOrWhiteSpace(entry.Id));
        }
    }
}
