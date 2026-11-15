using System.Linq;
using Cybersole.Ui.Views.Accounts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R332: the fourteen platform names in the accounts left pane, pinned against the running 5.18.32 build.
///
/// <para>
/// This list is user-visible text in a fixed order, so it is exactly the kind of thing that drifts quietly: a rename, a
/// stray space ("Pop Mart" for "Popmart"), or a reordering would look fine in code and wrong on screen. The order below
/// was read off the live Accounts page in R332, top to bottom.
/// </para>
/// </summary>
public sealed class AccountStoreListTests
{
    private readonly ITestOutputHelper _out;
    public AccountStoreListTests(ITestOutputHelper output) => _out = output;

    private static readonly string[] Live =
    {
        "Nike", "Nike GS", "Shopify", "Footlocker (Asia)", "Farfetch", "Demandware (Funko)",
        "Demandware", "Magento", "Casio", "HBX", "Popmart", "Goat", "Scheels", "Warhammer",
    };

    [Fact]
    public void ThePlatformsAreTheFourteenTheLivePageShows()
    {
        _out.WriteLine(string.Join(" | ", Platforms()));

        Assert.Equal(Live, Platforms());
    }

    [Fact]
    public void TwoDemandwareEntriesAndTwoNikeEntriesStayDistinct()
    {
        var platforms = Platforms();

        Assert.Contains("Nike", platforms);
        Assert.Contains("Nike GS", platforms);
        Assert.Contains("Demandware", platforms);
        Assert.Contains("Demandware (Funko)", platforms);
        Assert.Equal(platforms.Length, platforms.Distinct().Count());
    }

    private static string[] Platforms() =>
        StoreCatalog.Platforms.ToArray();
}
