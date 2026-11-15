using Cybersole.Stores.Flows;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 136: the image gets a Kasada token four ways, and the replica only had one.
///
/// <para>
/// The status strings settle it. "Getting Kasada" and "solving Kasada" are different verbs — the first
/// asks a service, the second runs the page — and both have failure messages, including
/// <c>Kasada API down (Contact staff)</c>, which only makes sense if a service exists. On top of those
/// sit two named fallbacks, <c>Kasada-Fallback</c> and <c>Kasada-Mobile-Fallback</c>, and an interface,
/// <c>IKasadaSolver</c>, which is why the modes can be swapped at all.
/// </para>
///
/// <para>
/// These strings are user-visible, so they are a contract: a replica that invents its own wording
/// looks different for no reason.
/// </para>
/// </summary>
public sealed class KasadaStrategyTests
{
    private readonly ITestOutputHelper _out;

    public KasadaStrategyTests(ITestOutputHelper output) => _out = output;

    /// <summary>Four modes, four verbs.</summary>
    [Fact]
    public void ThereAreFourModesWithDistinctVerbs()
    {
        Assert.Equal("getting", KasadaStrategy.Verb(KasadaStrategy.Mode.Api));
        Assert.Equal("solving", KasadaStrategy.Verb(KasadaStrategy.Mode.Local));
        Assert.Equal("falling back to", KasadaStrategy.Verb(KasadaStrategy.Mode.Fallback));
        Assert.Equal("falling back to", KasadaStrategy.Verb(KasadaStrategy.Mode.MobileFallback));

        foreach (var mode in System.Enum.GetValues<KasadaStrategy.Mode>())
        {
            Assert.True(KasadaStrategy.IsUsable(mode), mode.ToString());
            _out.WriteLine($"{mode,-16} {KasadaStrategy.Verb(mode)}");
        }
    }

    /// <summary>Every status string is recorded verbatim.</summary>
    [Fact]
    public void TheStatusesAreRecorded()
    {
        Assert.Equal(12, KasadaStrategy.Statuses.Count);

        foreach (var (status, meaning) in KasadaStrategy.Statuses)
            _out.WriteLine($"{status,-36} {meaning}");

        Assert.Contains("Kasada API down (Contact staff)", KasadaStrategy.StatusList);
        Assert.Contains("Getting Kasada (MFC)", KasadaStrategy.StatusList);
        Assert.Contains("Failed Kasada (Retry limit reached)", KasadaStrategy.StatusList);
    }

    /// <summary>A status maps back to the mode that produced it.</summary>
    [Fact]
    public void StatusesMapBackToTheirMode()
    {
        Assert.Equal(KasadaStrategy.Mode.Api, KasadaStrategy.ModeFor("Getting Kasada (1)"));
        Assert.Equal(KasadaStrategy.Mode.Api, KasadaStrategy.ModeFor("Failed getting Kasada (Rotating)"));
        Assert.Equal(KasadaStrategy.Mode.Local, KasadaStrategy.ModeFor("Failed solving Kasada (TL)"));
        Assert.Equal(KasadaStrategy.Mode.Api, KasadaStrategy.ModeFor("Kasada API down (Contact staff)"));
        Assert.Equal(KasadaStrategy.Mode.MobileFallback, KasadaStrategy.ModeFor("Getting Kasada (MFC)"));

        Assert.Null(KasadaStrategy.ModeFor("Something else"));
        Assert.Null(KasadaStrategy.ModeFor(null));
    }

    /// <summary>The two fallbacks are named, which is how a caller knows which one it got.</summary>
    [Fact]
    public void TheFallbacksAreNamed()
    {
        Assert.Equal("Kasada-Fallback", KasadaStrategy.Fallback);
        Assert.Equal("Kasada-Mobile-Fallback", KasadaStrategy.MobileFallback);
        Assert.True(KasadaStrategy.ModeFor(KasadaStrategy.Fallback) is not null);
    }

    /// <summary>The version header is per store — a table, not a constant.</summary>
    [Fact]
    public void TheVersionHeaderIsPerStore()
    {
        Assert.Equal(7, KasadaStrategy.VersionHeaders.Count);
        foreach (var header in KasadaStrategy.VersionHeaders)
        {
            Assert.EndsWith("-Kasada-Version", header, System.StringComparison.Ordinal);
            _out.WriteLine(header);
        }

        // and the store whose version header exists is the store the session already models
        Assert.Equal("Nike-Kasada-Version", NikeHeaders.KasadaVersion);
    }

    /// <summary>Eight protocol headers, all <c>x-kpsdk-</c>.</summary>
    [Fact]
    public void TheProtocolHeadersAreEight()
    {
        Assert.Equal(8, KasadaStrategy.ProtocolHeaders.Count);
        Assert.All(KasadaStrategy.ProtocolHeaders,
            h => Assert.StartsWith("x-kpsdk-", h, System.StringComparison.Ordinal));
        Assert.Equal(8, KasadaStrategy.ProtocolHeaders.Distinct().Count());
    }

    /// <summary>The interface the image declares is the reason the modes are interchangeable.</summary>
    [Fact]
    public void TheImageDeclaresASolverInterface()
    {
        Assert.Equal("IKasadaSolver", KasadaStrategy.SolverInterface);
        _out.WriteLine("the replica's ChromiumKasadaSolver is one implementation of " +
                       KasadaStrategy.SolverInterface);
    }
}
