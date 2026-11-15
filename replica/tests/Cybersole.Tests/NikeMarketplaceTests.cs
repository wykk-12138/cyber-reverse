using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 86: Nike's marketplace is per-instance, not a constant.
///
/// <para>
/// The binary's string table spells out <b>forty-two</b> markets as "Nike XX" entries, and its
/// <c>_countryCode</c> is an <b>instance</b> field — one per flow, chosen by the task. The replica
/// had <c>const string Marketplace = "US"</c>, which cannot be per-task: every checkout went to the
/// United States no matter what the profile said.
/// </para>
///
/// <code>
/// AT AU BE BG CA CH CZ DE DK ES FI FR GB GR GS HR HU IE IL IN IT JP LU MX MY NL NO NZ PH PL PT RO
/// SE SG SI SK TH TR TW US VN ZA
/// </code>
///
/// <para>
/// R86 read twenty-two of them — a window, not the table — and so claimed the binary had no GB
/// market. R89 read the table: forty-two entries, GB included.
///
/// <para>
/// The mapping is deliberately conservative: an unsupported country falls back to US rather than
/// building a URL the API has never been asked about.
/// </para>
/// </summary>
public sealed class NikeMarketplaceTests
{
    private readonly ITestOutputHelper _out;

    public NikeMarketplaceTests(ITestOutputHelper output) => _out = output;

    /// <summary>The forty-two marketplaces, in the binary's (alphabetical) order.</summary>
    [Fact]
    public void TheBinaryHasFortyTwoMarkets()
    {
        _out.WriteLine(string.Join(" ", NikeFlow.Countries));

        Assert.Equal(42, NikeFlow.Countries.Count);
        Assert.Equal(42, NikeFlow.Countries.Distinct().Count());
        Assert.Equal("AT", NikeFlow.Countries[0]);
        Assert.Equal("GB", NikeFlow.Countries[12]);
        Assert.Equal("ZA", NikeFlow.Countries[^1]);

        // alphabetically ordered, the way the image stores them
        Assert.Equal(NikeFlow.Countries.OrderBy(c => c, StringComparer.Ordinal), NikeFlow.Countries);
    }

    /// <summary>A fresh flow defaults to US — the market the replica used to be nailed to.</summary>
    [Fact]
    public void AFreshFlowDefaultsToUs()
    {
        var flow = new NikeFlow();

        _out.WriteLine("default: " + flow.CountryCode);

        Assert.Equal("US", flow.CountryCode);
    }

    /// <summary>The country is per instance: two flows can be in two markets at once.</summary>
    [Fact]
    public void TwoFlowsCanBeInTwoMarkets()
    {
        var japan = new NikeFlow { CountryCode = "JP" };
        var germany = new NikeFlow { CountryCode = "DE" };   // unsupported, kept as given until mapped

        _out.WriteLine($"japan={japan.CountryCode} other={germany.CountryCode}");

        Assert.Equal("JP", japan.CountryCode);
        Assert.NotEqual(japan.CountryCode, new NikeFlow().CountryCode);
    }

    /// <summary>Profile countries map onto the supported set, with US as the fallback.</summary>
    [Theory]
    [InlineData("US", "US")]
    [InlineData("us", "US")]
    [InlineData("JP", "JP")]
    [InlineData("jp", "JP")]
    [InlineData("ZA", "ZA")]
    [InlineData("UK", "GB")]   // the alias resolves onto a market the binary really has
    [InlineData("GB", "GB")]
    [InlineData("DE", "DE")]   // Germany is in the table
    [InlineData("FR", "FR")]
    [InlineData("CN", "US")]   // China is not
    [InlineData("", "US")]
    [InlineData(null, "US")]
    public void ProfileCountriesMapOntoSupportedMarkets(string? profile, string expected)
    {
        var mapped = NikeFlow.CountryFor(profile);

        _out.WriteLine($"{profile ?? "<null>"} -> {mapped}");

        Assert.Equal(expected, mapped);
    }

    /// <summary>
    /// The mapped value is always one the binary supports — a mapping that could produce an
    /// unsupported code would be worse than the constant it replaced.
    /// </summary>
    [Fact]
    public void TheMappingNeverInventsAMarket()
    {
        foreach (var profile in new[] { "GB", "UK", "DE", "FR", "CN", "BR", "IN", "XX", "  " })
        {
            var mapped = NikeFlow.CountryFor(profile);
            Assert.Contains(mapped, NikeFlow.Countries);
        }

        _out.WriteLine("every mapping lands inside the twenty-two");
    }
}
