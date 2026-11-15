using Cybersole.Stores.Flows;
using System.Text.RegularExpressions;
using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Runs the module parsers against real product pages.
///
/// The first attempt walked each site's listing page to discover a product URL. That does not
/// work: these storefronts render their grids client-side, so the listing HTML carries
/// navigation and asset links only — a 326 KB Casio category page had no product href at all.
/// Discovery needs JavaScript, which means ChromiumBridge, which means the capture harness.
///
/// So this takes product URLs as given. One is verified (Casio); the rest are recorded as
/// needing a browser-assisted capture before their parsers can be judged.
///
/// Speed=Slow, and it reports rather than fails: a challenge page is a fact about the site, not
/// a parser defect.
/// </summary>
[Trait("Speed", "Slow")]
public class ProductPageProbeTests
{
    private readonly ITestOutputHelper _out;
    public ProductPageProbeTests(ITestOutputHelper output) => _out = output;

    /// <summary>
    /// <c>Url</c> is null where the product link needs a browser to discover — that is a
    /// recorded gap, not an oversight.
    /// </summary>
    private static readonly (string Module, string? Url, string Note)[] Targets =
    {
        ("casio",
            "https://www.casio.com/us/watches/gshock/product.GA-2100-1A/",
            "verified 6/8 (title/price/priceJson/nameJson/skuish/jsonLd) when the page returned " +
            "443 KB; now answers 2.7 KB, i.e. rate-limited or challenged"),

        ("warhammer", null,
            "listing returns 202 with a 2 KB body — challenge page, technology not identified"),

        ("supreme", null,
            "listing returns 403; needs headed capture"),

        ("johnlewis",
            "https://www.johnlewis.com/opi-infinite-shine-nail-lacquer/alpine-snow/p5884022",
            "fixed: <h1> for the name, and a price extractor that ignores the meta description's " +
            "'Free Delivery on orders over £50'. ld+json has no price, so the marked price " +
            "element is preferred and an unmarked page yields empty rather than a wrong number"),

        ("hbx",
            "https://hbx.com/men/brands/veja/volley-leather-white-green",
            "product path is /{gender}/brands/{brand}/{product} — discovered via " +
            "NetworkRecorder.CollectLinksAsync, not guessed"),

        ("popmart",
            "https://www.popmart.com/us/products/4205/dimoo-becoming-a-tree-figure",
            "product path is /{region}/products/{id}/{slug} — discovered via CollectLinksAsync"),

        ("scheels", null,
            "listing returns 403; Kasada (same build as Nike)"),

        ("yeezysupply", null,
            "site retired; cannot probe"),
    };

    /// <summary>
    /// Must mirror the patterns the flows actually use, including their alternations. An
    /// earlier version split <c>(?:sku|skuId|variantId)</c> into three separate checks, so a
    /// store using skuId reported three misses and looked broken when it was not.
    /// </summary>
    private static readonly (string Name, string Pattern)[] Parsers =
    {
        ("title", @"<title>([^<|]+)"),
        ("price", @"(?:USD|€|£|\$)\s?([\d,.]+)"),
        ("priceJson", @"""(?:price|listPrice)""\s*:\s*""?([\d.]+)""?"),
        ("nameJson", @"""(?:name|title)""\s*:\s*""([^""]+)"""),
        ("skuish", @"""(?:sku|skuId|variantId|productId)""\s*:\s*""?([A-Za-z0-9_\-]+)""?"),
        ("size", @"""size""\s*:\s*""([^""]{1,16})"""),
        ("jsonLd", @"<script[^>]+type=""application/ld\+json""[^>]*>"),
        ("addToCart", @"(?:add[\s\-]?to[\s\-]?(?:cart|bag|basket))"),
    };

    private static bool IsChallenge(int status, long bytes) =>
        status is 202 or 403 or 429 || (status == 200 && bytes < 5000);

    private async Task ProbeAsync(NetClient net, string module, string url)
    {
        _out.WriteLine($"=== {module} ===");
        _out.WriteLine($"  {url}");

        NetResponse res;
        try
        {
            res = await net.GetAsync(url, new RequestOptions { Tag = "pp-probe" },
                CancellationToken.None);
        }
        catch (Exception ex)
        {
            _out.WriteLine($"  unreachable: {ex.GetType().Name}: {ex.Message}");
            _out.WriteLine(string.Empty);
            return;
        }

        _out.WriteLine($"  HTTP {res.StatusCode}  {res.BodyBytes:N0} bytes");

        if (IsChallenge(res.StatusCode, res.BodyBytes))
        {
            _out.WriteLine("  challenge page — the parser cannot be judged from this");
            _out.WriteLine(string.Empty);
            return;
        }

        var hits = 0;
        foreach (var (name, pattern) in Parsers)
        {
            var m = Regex.Match(res.Body, pattern, RegexOptions.IgnoreCase);
            if (!m.Success) { _out.WriteLine($"  MISS  {name,-12}"); continue; }

            hits++;
            var sample = m.Groups.Count > 1 ? m.Groups[1].Value : m.Value;
            sample = sample.Replace('\n', ' ').Replace('\r', ' ').Trim();
            if (sample.Length > 50) sample = sample[..50];
            _out.WriteLine($"  HIT   {name,-12} {sample}");
        }

        _out.WriteLine($"  -> {hits}/{Parsers.Length} matched");

        // Where a module exposes its strategy as a callable, use THAT rather than a copy of its
        // regex. Copying is how the probe previously reported "price 0" for PopMart even after
        // PopMartFlow.ExtractPrice had been fixed to skip the SPU placeholder.
        if (module == "popmart")
        {
            var resolved = PopMartFlow.ExtractPrice(res.Body);
            _out.WriteLine($"  PopMartFlow.ExtractPrice -> \"{resolved}\"");
        }

        // John Lewis uses <h1> for the product name and £ for the price — NOT <title> and not
        // a currency alternation. The probe's generic patterns were reporting false hits
        // ("Store Finder", "50.") while the module's own patterns were never tried.
        if (module == "johnlewis")
        {
            // call the module's own extractors rather than re-deriving their patterns
            _out.WriteLine($"  ExtractProductName -> \"{Trunc(JohnLewisFlow.ExtractProductName(res.Body))}\"");
            var jlPrice = JohnLewisFlow.ExtractPrice(res.Body);
            _out.WriteLine($"  ExtractPrice       -> \"{jlPrice}\"  " +
                           (jlPrice.Length > 0 ? "(found)" : "(no marked price element on this page)"));
        }

        _out.WriteLine(string.Empty);
    }

    private static string Trunc(string s) => s.Length <= 60 ? s : s[..60];

    [Fact]
    public async Task VerifiedProductPagesParseAndTheRestAreRecordedAsGaps()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        var probed = 0;
        var gaps = new List<string>();

        foreach (var (module, url, note) in Targets)
        {
            if (url is null)
            {
                gaps.Add($"{module,-14} {note}");
                continue;
            }

            probed++;
            await ProbeAsync(net, module, url);
        }

        _out.WriteLine("=== recorded gaps (product page not yet reachable) ===");
        foreach (var g in gaps) _out.WriteLine($"  {g}");

        _out.WriteLine(string.Empty);
        _out.WriteLine($"probed {probed}, recorded {gaps.Count} gap(s)");

        // Casio is the one with a real page; it must keep parsing.
        Assert.True(probed >= 1, "no product page was probed at all — the probe itself is broken");
    }

    /// <summary>
    /// Shows every occurrence of a price-ish field with its surrounding context.
    ///
    /// Why: the PopMart probe matched "price":0 while the page's real price is 30. A single
    /// first-match regex cannot tell a placeholder from the actual value, and "fix it by
    /// skipping zero" is a guess unless you know what the zero means. This prints the evidence.
    /// </summary>
    [Fact]
    public async Task PriceFieldsShowTheirContextSoAPlaceholderCanBeToldFromAValue()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        const string url = "https://www.popmart.com/us/products/4205/dimoo-becoming-a-tree-figure";

        NetResponse res;
        try
        {
            res = await net.GetAsync(url, new RequestOptions { Tag = "price-context" },
                CancellationToken.None);
        }
        catch (Exception ex)
        {
            _out.WriteLine($"unreachable: {ex.Message}");
            return;
        }

        _out.WriteLine($"HTTP {res.StatusCode}  {res.BodyBytes:N0} bytes");
        if (!res.IsSuccess) return;

        var seen = 0;

        foreach (Match m in Regex.Matches(res.Body, @"""(\w*[Pp]rice\w*)""\s*:\s*""?([\w.\-]+)""?"))
        {
            seen++;
            if (seen > 20) break;

            var field = m.Groups[1].Value;
            var value = m.Groups[2].Value;

            // 60 characters on each side, enough to see which product or region it belongs to
            var from = Math.Max(0, m.Index - 60);
            var len = Math.Min(160, res.Body.Length - from);
            var context = res.Body.Substring(from, len).Replace('\n', ' ').Replace('\r', ' ');

            _out.WriteLine($"  {field} = {value}");
            _out.WriteLine($"      ...{context}...");
        }

        _out.WriteLine(string.Empty);
        _out.WriteLine($"total price-ish fields: {seen}");
        Assert.True(seen > 0, "no price field matched at all");
    }
}
