using System.Linq;
using Cybersole.Core.Models;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// StartupPage's values, which the image does not carry as strings, and the one place the replica disagrees with the
/// navigation it names.
///
/// <para>
/// R931. Searching the image for StartupPage returns the type name, the binding descriptors, the backing field and the
/// locale entry <c>Settings.General.StartupPage</c> with its tooltip — but no member names. So the values cannot be read
/// the way ConcurrencyMode's almost were; what can be read is the navigation, because the locale names exactly six
/// destinations: Home, Tasks, Proxies, Billing, Accounts and Settings.
/// </para>
///
/// <para>
/// The replica's enum has six values too, and five of them match. The fifth is Analytics where the navigation says
/// Billing. That is a real disagreement and it is pinned rather than resolved, because the evidence says what the
/// navigation offers and not what an ordering means: AnalyticsView exists in the resource index, so both screens exist,
/// and whether StartupPage.Billing is the key that opens Analytics — or whether the replica's Analytics value is simply
/// a rename of Billing — cannot be settled from names alone.
/// </para>
/// </summary>
public class StartupPageTests
{
    /// <summary>The six destinations the locale names, in the order the navigation lists them.</summary>
    private static readonly string[] NavPages = { "Home", "Tasks", "Proxies", "Billing", "Accounts", "Settings" };

    /// <summary>Six values, which is the count the navigation implies.</summary>
    [Fact]
    public void TheEnumHasSixValues()
    {
        Assert.Equal(6, System.Enum.GetValues<StartupPage>().Length);
        Assert.Equal(6, NavPages.Length);
    }

    /// <summary>
    /// Five of the six names match the navigation exactly. Listed rather than counted, so a rename of one into another
    /// cannot keep the total at five.
    /// </summary>
    [Fact]
    public void FiveNamesMatchTheNavigation()
    {
        var names = System.Enum.GetNames<StartupPage>().ToHashSet();
        var shared = NavPages.Where(names.Contains).OrderBy(n => n).ToArray();

        Assert.Equal(new[] { "Accounts", "Home", "Proxies", "Settings", "Tasks" }, shared);
    }

    /// <summary>
    /// The disagreement, pinned: the navigation says Billing and the enum says Analytics. Pinned instead of fixed because
    /// the recovered evidence says which pages the navigation offers, not which value a startup choice stores — and
    /// AnalyticsView exists in the resource index, so both screens are real.
    /// </summary>
    [Fact]
    public void TheFifthNameDisagreesAndThatIsRecorded()
    {
        var names = System.Enum.GetNames<StartupPage>();

        Assert.Contains("Analytics", names);
        Assert.DoesNotContain("Billing", names);
        Assert.Contains("Billing", NavPages);
        Assert.DoesNotContain("Analytics", NavPages);
    }

    /// <summary>
    /// Home is the default, and it is the one value both sources agree on and that a fresh settings file can hold
    /// without choosing anything.
    /// </summary>
    [Fact]
    public void HomeIsTheZeroValue()
    {
        Assert.Equal(0, (int)StartupPage.Home);
        Assert.Equal(StartupPage.Home, default(StartupPage));
    }
}