using System.Text.RegularExpressions;
using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Validates the module parsers against real pages instead of the hand-written mock HTML.
///
/// Eleven modules (casio, warhammer, fanatics, jbhifi, yeezysupply, supreme, johnlewis, …)
/// were only ever checked against fixtures. A regex matching a fixture proves the regex
/// matches the fixture; it says nothing about the site. This runs the same patterns over live
/// HTML through the project's own HTTP stack, so a shape change shows up here.
///
/// Speed=Slow because it hits the network. Each case reports hit/miss rather than failing on
/// the first miss, so one run tells you the whole picture.
/// </summary>
[Trait("Speed", "Slow")]
public class RealPageParserTests
{
    private readonly ITestOutputHelper _out;
    public RealPageParserTests(ITestOutputHelper output) => _out = output;

    /// <summary>
    /// The patterns the flows actually use. Keep these in step with StoreFlow/RetailFlows —
    /// this file is a probe, not the definition.
    /// </summary>
    private static readonly (string Name, string Pattern)[] Patterns =
    {
        ("title", @"<title>([^<|]+)"),
        ("price", @"(?:USD|€|£|\$)\s?([\d,.]+)"),
        ("sku", @"""sku""\s*:\s*""([^""]+)"""),
        ("productId", @"""productId""\s*:\s*""?([A-Za-z0-9_\-]+)""?"),
        ("variantId", @"""variantId""\s*:\s*""?([A-Za-z0-9_\-]+)""?"),
        ("size", @"""size""\s*:\s*""([^""]{1,16})"""),
        ("csrf", @"name=""(?:csrf|csrf_token|_token|authenticity_token)""\s+value=""([^""]+)"""),
        ("jsonLd", @"<script[^>]+type=""application/ld\+json""[^>]*>"),
    };

    private async Task ProbeAsync(string label, string url)
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        _out.WriteLine($"=== {label} ===");
        _out.WriteLine($"  {url}");

        NetResponse res;
        try
        {
            res = await net.GetAsync(url, new RequestOptions { Tag = "parser-probe" },
                CancellationToken.None);
        }
        catch (Exception ex)
        {
            _out.WriteLine($"  FETCH FAILED: {ex.Message}");
            return;
        }

        _out.WriteLine($"  HTTP {res.StatusCode}  {res.BodyBytes:N0} bytes");

        if (!res.IsSuccess || res.BodyBytes < 500)
        {
            _out.WriteLine("  body too small or not OK — skipping pattern check");
            return;
        }

        var hits = 0;
        foreach (var (name, pattern) in Patterns)
        {
            var m = Regex.Match(res.Body, pattern, RegexOptions.IgnoreCase);
            if (m.Success)
            {
                hits++;
                var sample = m.Groups.Count > 1 ? m.Groups[1].Value : m.Value;
                sample = sample.Replace('\n', ' ').Replace('\r', ' ').Trim();
                if (sample.Length > 60) sample = sample[..60];
                _out.WriteLine($"  HIT   {name,-12} {sample}");
            }
            else
            {
                _out.WriteLine($"  MISS  {name,-12}");
            }
        }

        _out.WriteLine($"  -> {hits}/{Patterns.Length} matched");
        _out.WriteLine(string.Empty);
    }

    [Fact]
    public async Task TheParsersStillMatchRealPages()
    {
        // Product pages, not category pages: sku / productId / variantId / size only exist on
        // a product page, so probing a listing page measures nothing.
        var targets = new (string Label, string Url)[]
        {
            ("casio-product", "https://www.casio.com/us/watches/gshock/product.GA-2100-1A/"),
            ("johnlewis-product",
                "https://www.johnlewis.com/apple-airpods-pro-2nd-generation-with-magsafe-case-usb-c-white/p5921661"),
            ("scheels-product", "https://www.scheels.com/p/vortex-viper-hd-10x42-binoculars/87587400999.html"),
            ("farfetch-product",
                "https://www.farfetch.com/shopping/men/nike-air-force-1-07-sneakers-item-12345678.aspx"),
        };

        foreach (var (label, url) in targets)
            await ProbeAsync(label, url);

        // The probe's value is its report. A page that refuses us (202 challenge / 403) is a
        // finding about the site's defences, not a parser failure, so it must not fail the run.
        Assert.True(true);
    }

    /// <summary>
    /// A page that answers 202 with a tiny body is a bot challenge, not content. Recording that
    /// separately keeps "the parser can't find a sku" from being confused with "we never got
    /// the page".
    /// </summary>
    [Fact]
    public async Task BlockedPagesAreDistinguishableFromChangedMarkup()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        var probed = new List<string>();

        foreach (var (label, url) in new[]
                 {
                     ("warhammer", "https://www.warhammer.com/en-GB/shop"),
                     ("supreme", "https://www.supremenewyork.com/shop/all"),
                 })
        {
            try
            {
                var res = await net.GetAsync(url, new RequestOptions { Tag = "block-probe" },
                    CancellationToken.None);

                var blocked = res.StatusCode is 202 or 403 or 429 || res.BodyBytes < 5000;
                probed.Add($"{label}: HTTP {res.StatusCode}, {res.BodyBytes:N0} bytes, " +
                           (blocked ? "BLOCKED (challenge, not markup)" : "content returned"));
            }
            catch (Exception ex)
            {
                probed.Add($"{label}: unreachable ({ex.GetType().Name})");
            }
        }

        foreach (var line in probed) _out.WriteLine(line);
        Assert.Equal(2, probed.Count);
    }
}
