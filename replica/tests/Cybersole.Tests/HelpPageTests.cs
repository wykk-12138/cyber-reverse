using Avalonia.Controls;
using Cybersole.Stores.Flows;
using Cybersole.Ui.Views.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 81: Get Help is the error index, and the index already existed.
///
/// <para>
/// The live page is one full-width <c>Open help center</c>, one <c>Search errors</c> field and
/// <b>thirteen</b> entries, each a bracketed title over its explanation:
/// </para>
///
/// <code>
/// [General]   Connection Error / Not found / Service Unavailable / Rate Limit /
///             Forbidden / Task failed                                   (6)
/// [Shopify]   Error Submitting Shipping (Handle Error) /
///             Error Submitting Order (Rate Limit) / Payment Error /
///             Connection Errors / Tasks hanging on "Getting Shipping Rates" /
///             Invalid Credit Card Number/Billing                        (6)
/// [Footsites] Rate Limit / 429                                         (1)
/// </code>
///
/// <para>
/// <c>ErrorCatalog.All</c> already carried all thirteen verbatim; <c>HelpView</c> rendered none of
/// them and said "there is no error index to search". This pins both halves: the catalogue's order
/// and the page actually printing it.
/// </para>
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class HelpPageTests
{
    private readonly ITestOutputHelper _out;

    public HelpPageTests(ITestOutputHelper output) => _out = output;

    /// <summary>The thirteen titles, in the live page's order.</summary>
    [Fact]
    public void TheCatalogueHasTheThirteenLiveEntries()
    {
        var titles = ErrorCatalog.All.Select(e => e.Title).ToList();
        foreach (var title in titles) _out.WriteLine(title);

        Assert.Equal(13, titles.Count);
        Assert.Equal(new[]
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
        }, titles);

        Assert.Equal(6, ErrorCatalog.Tagged("General").Count());
        Assert.Equal(6, ErrorCatalog.Tagged("Shopify").Count());
        Assert.Equal(1, ErrorCatalog.Tagged("Footsites").Count());
    }

    /// <summary>Four of the details, verbatim — typos included, because the original has them.</summary>
    [Theory]
    [InlineData("general.taskfailed",
        "The task hit a unrecoverable error. Please make sure that it's configured properly " +
        "and that all profile data is filled in and correct.")]
    [InlineData("shopify.connection",
        "Your proxies are randomly disconnecting/having issues connecting to the site. This can " +
        "also happen if you have not authenticated your IP for your IP auth proxies.")]
    [InlineData("shopify.card.invalid",
        "Your credit card number/billing is invalid or Shopify is returning that from their end. " +
        "It is not bot related.")]
    [InlineData("footsites.ratelimit",
        "Status code used for a multitude of errors. Ranging from product blocks to IP / ASN blacklist.")]
    public void TheDetailsAreVerbatim(string id, string detail)
    {
        var entry = ErrorCatalog.ById(id);

        Assert.NotNull(entry);
        _out.WriteLine($"{id}: {entry!.Detail}");
        Assert.Equal(detail, entry.Detail);
    }

    /// <summary>The page prints all thirteen, and its two controls, with no leftover button row.</summary>
    [Fact]
    public void ThePagePrintsTheWholeIndex()
    {
        var services = TestServices.Create();
        var view = new HelpView(services);

        var texts = Descendants(view).OfType<TextBlock>().Select(t => t.Text ?? "").ToList();
        var buttons = Descendants(view).OfType<Button>().Select(b => b.Content?.ToString() ?? "").ToList();

        foreach (var entry in ErrorCatalog.All)
        {
            Assert.Contains(entry.Title, texts);
            Assert.Contains(entry.Detail, texts);
        }

        Assert.Contains(HelpView.OpenCenterLabel, buttons);
        _out.WriteLine($"texts={texts.Count} buttons={buttons.Count}");

        // the old three-button row is gone
        Assert.DoesNotContain("Open community", buttons);
        Assert.DoesNotContain("Search errors", buttons);
    }

    /// <summary>The search field filters the index — that is what the live "Search errors" does.</summary>
    [Fact]
    public void TheSearchFiltersTheIndex()
    {
        Assert.Equal(13, HelpView.Filter(null).Count);
        Assert.Equal(13, HelpView.Filter("   ").Count);

        var shopify = HelpView.Filter("shopify");
        var footsites = HelpView.Filter("footsites");
        var proxies = HelpView.Filter("proxies");

        _out.WriteLine($"shopify={shopify.Count} footsites={footsites.Count} proxies={proxies.Count}");

        Assert.Equal(6, shopify.Count);
        Assert.Single(footsites);
        Assert.Equal(2, proxies.Count);      // Connection Error + Shopify Connection Errors
        Assert.Empty(HelpView.Filter("zzzz"));
    }

    // ---------------------------------------------------------------- helpers

    private static IEnumerable<Control> Descendants(Control root)
    {
        var queue = new Queue<Control>();
        queue.Enqueue(root);
        while (queue.Count > 0)
        {
            var current = queue.Dequeue();
            if (!ReferenceEquals(current, root)) yield return current;

            foreach (var child in Avalonia.LogicalTree.LogicalExtensions
                         .GetLogicalChildren(current).OfType<Control>())
                queue.Enqueue(child);
        }
    }
}
