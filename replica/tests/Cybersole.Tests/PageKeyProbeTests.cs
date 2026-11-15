using System.Text.RegularExpressions;
using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Dumps the JSON key names present on a storefront page.
///
/// HBX's product page has no <c>size</c> key and no sku-ish key at all, in 266 KB of HTML.
/// Before concluding "the data is not there", it is worth seeing what the page DOES carry —
/// the payload may be gzipped inside a script, or keyed in a vocabulary the flows do not
/// expect (colourways, style codes, barcodes).
///
/// Speed=Slow, network-bound.
/// </summary>
[Trait("Speed", "Slow")]
public class PageKeyProbeTests
{
    private readonly ITestOutputHelper _out;
    public PageKeyProbeTests(ITestOutputHelper output) => _out = output;

    private const string HbxProduct =
        "https://hbx.com/men/brands/veja/volley-leather-white-green";

    private static readonly Regex JsonKey = new(@"""([A-Za-z_$][\w$]{1,40})""\s*:", RegexOptions.Compiled);

    [Fact]
    public async Task TheProductPageShowsWhatKeysItActuallyHas()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        NetResponse res;
        try
        {
            res = await net.GetAsync(HbxProduct, new RequestOptions { Tag = "key-probe" },
                CancellationToken.None);
        }
        catch (Exception ex)
        {
            _out.WriteLine($"unreachable: {ex.Message}");
            return;
        }

        _out.WriteLine($"HTTP {res.StatusCode}  {res.BodyBytes:N0} bytes");
        if (!res.IsSuccess) return;

        var counts = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);

        foreach (Match m in JsonKey.Matches(res.Body))
        {
            var k = m.Groups[1].Value;
            counts[k] = counts.TryGetValue(k, out var n) ? n + 1 : 1;
        }

        _out.WriteLine($"distinct JSON keys: {counts.Count}");
        _out.WriteLine(string.Empty);

        foreach (var (k, n) in counts.OrderByDescending(kv => kv.Value).Take(60))
            _out.WriteLine($"  {n,4}  {k}");

        // script tags: is there an embedded state blob at all?
        _out.WriteLine(string.Empty);
        var scripts = Regex.Matches(res.Body, @"<script([^>]*)>")
            .Select(m => m.Groups[1].Value)
            .Where(a => a.Contains("json", StringComparison.OrdinalIgnoreCase)
                        || a.Contains("state", StringComparison.OrdinalIgnoreCase)
                        || a.Contains("data", StringComparison.OrdinalIgnoreCase))
            .Distinct()
            .Take(10)
            .ToList();

        _out.WriteLine($"script tags that look like state carriers: {scripts.Count}");
        foreach (var s in scripts) _out.WriteLine($"  <script{s}>");

        Assert.True(counts.Count >= 0);
    }
}
