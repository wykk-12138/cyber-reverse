using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 166: where the other twenty-two names live, and what that split means.
///
/// <para>
/// The census divides the fifty recorded names three ways: twenty-seven the engine carries, ten inherited from
/// <c>Object.prototype</c>, thirteen a phone has and this engine does not. That third group is the mirror of
/// <see cref="NavPrune"/> — one measurement, read in opposite directions: prune what the engine has and a phone
/// lacks, install what a phone has and the engine lacks.
/// </para>
/// </summary>
public sealed class NavigatorCensusTests
{
    private readonly ITestOutputHelper _out;

    public NavigatorCensusTests(ITestOutputHelper output) => _out = output;

    /// <summary>Fifty names, three homes, twenty-seven / ten / thirteen.</summary>
    [Fact]
    public void TheCensusAddsUp()
    {
        Assert.Equal(50, NavigatorCensus.Measured.Count);
        Assert.Equal(27, NavigatorCensus.Present.Count);
        Assert.Equal(10, NavigatorCensus.Inherited.Count);
        Assert.Equal(13, NavigatorCensus.Missing.Count);
        Assert.Equal(50,
            NavigatorCensus.Present.Count + NavigatorCensus.Inherited.Count + NavigatorCensus.Missing.Count);

        // the census covers exactly the recorded names, no more
        Assert.Empty(MobileNavigator.NavOrder.Where(n => !NavigatorCensus.Measured.ContainsKey(n)));

        _out.WriteLine("missing: " + string.Join(", ", NavigatorCensus.Missing));
    }

    /// <summary>The inherited ten are the Object.prototype members, and nothing here touches them.</summary>
    [Fact]
    public void TheInheritedTenAreObjectPrototype()
    {
        Assert.Contains("toString", NavigatorCensus.Inherited);
        Assert.Contains("valueOf", NavigatorCensus.Inherited);
        Assert.Contains("hasOwnProperty", NavigatorCensus.Inherited);
        Assert.Contains("__lookupSetter__", NavigatorCensus.Inherited);

        Assert.Equal(10, NavigatorCensus.Inherited.Count);
    }

    /// <summary>The thirteen missing names are the install list, and two are installed now.</summary>
    [Fact]
    public void TheMissingThirteenAreTheInstallList()
    {
        Assert.Contains("standalone", NavigatorCensus.Missing);
        Assert.Contains("credentials", NavigatorCensus.Missing);
        Assert.Contains("mediaDevices", NavigatorCensus.Missing);

        Assert.Equal(new[] { "standalone", "locks" }, NavigatorCensus.InstalledNow);
        Assert.All(NavigatorCensus.InstalledNow, n => Assert.Contains(n, NavigatorCensus.Missing));
    }

    /// <summary>Every deferred name carries a reason, and the reasons are not "forgot".</summary>
    [Fact]
    public void TheDeferredNamesSayWhy()
    {
        var deferred = NavigatorCensus.Deferred.Keys.ToList();
        Assert.All(deferred, n => Assert.Contains(n, NavigatorCensus.Missing));

        // eleven deferred plus two installed covers the thirteen
        Assert.Equal(11, deferred.Count);
        Assert.Equal(13, deferred.Count + NavigatorCensus.InstalledNow.Count);

        foreach (var (name, reason) in NavigatorCensus.Deferred)
            _out.WriteLine($"{name,-30} {reason}");

        Assert.Contains("WebAuthn", NavigatorCensus.Deferred["credentials"]);

        // the serviceWorker reason says a shim that never registers is itself a tell; the word to look for is
        // the sentence the reason actually uses
        Assert.Contains("never registers", NavigatorCensus.Deferred["serviceWorker"]);
    }

    /// <summary>The two lists are one measurement read two ways.</summary>
    [Fact]
    public void TheTwoListsAreOneMeasurement()
    {
        // nothing is on both lists: pruned names are Blink-only, installed names are phone-only
        Assert.Empty(NavPrune.BlinkOnly.Intersect(
            NavigatorCensus.Missing, System.StringComparer.OrdinalIgnoreCase));

        Assert.Contains("opposite directions", NavigatorCensus.Rule);

        // and the one name that shows the asymmetry: connection is pruned, credentials is installed
        Assert.Contains("connection", NavPrune.BlinkOnly);
        Assert.Contains("credentials", NavigatorCensus.Missing);
    }
}
