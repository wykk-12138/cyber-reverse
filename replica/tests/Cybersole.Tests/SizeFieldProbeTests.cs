using System.Text.RegularExpressions;
using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Shows how a store represents per-size options.
///
/// HBX is a sneaker shop, so it must have sizes — yet the generic probe reports <c>size</c> as
/// a miss. Either the field is named differently, or sizes live in a separate request. This
/// prints the candidate fields so the difference can be seen rather than assumed.
///
/// Speed=Slow, network-bound.
/// </summary>
[Trait("Speed", "Slow")]
public class SizeFieldProbeTests
{
    private readonly ITestOutputHelper _out;
    public SizeFieldProbeTests(ITestOutputHelper output) => _out = output;

    private const string HbxProduct =
        "https://hbx.com/men/brands/veja/volley-leather-white-green";

    private const string PopMartProduct =
        "https://www.popmart.com/us/products/4205/dimoo-becoming-a-tree-figure";

    /// <summary>Anything that could carry a size or an option list.</summary>
    private static readonly Regex Sizeish = new(
        @"""([\w$]*(?:size|Size|option|Option|variant|Variant|stock|Stock|avail|Avail|qty|Qty)[\w$]*)""" +
        @"\s*:\s*(""[^""]{1,40}""|[\d.]+|true|false|null|\[|\{)",
        RegexOptions.IgnoreCase);

    private async Task ProbeAsync(NetClient net, string label, string url)
    {
        _out.WriteLine($"=== {label} ===");

        NetResponse res;
        try
        {
            res = await net.GetAsync(url, new RequestOptions { Tag = "size-probe" },
                CancellationToken.None);
        }
        catch (Exception ex)
        {
            _out.WriteLine($"  unreachable: {ex.GetType().Name}");
            _out.WriteLine(string.Empty);
            return;
        }

        _out.WriteLine($"  HTTP {res.StatusCode}  {res.BodyBytes:N0} bytes");
        if (!res.IsSuccess || res.BodyBytes < 5000)
        {
            _out.WriteLine("  challenge page");
            _out.WriteLine(string.Empty);
            return;
        }

        var seen = new Dictionary<string, List<string>>(StringComparer.OrdinalIgnoreCase);

        foreach (Match m in Sizeish.Matches(res.Body))
        {
            var name = m.Groups[1].Value;
            var value = m.Groups[2].Value;

            if (!seen.TryGetValue(name, out var list))
                seen[name] = list = new List<string>();

            if (list.Count < 4 && !list.Contains(value)) list.Add(value);
        }

        if (seen.Count == 0)
            _out.WriteLine("  no size-ish field at all");
        else
            foreach (var (name, values) in seen.OrderByDescending(kv => kv.Value.Count).Take(20))
                _out.WriteLine($"  {name,-26} {string.Join(" | ", values)}");

        // does the text "size" even appear as a JSON key?
        var keys = Regex.Matches(res.Body, @"""(\w*size\w*)\""\s*:")
            .Select(m => m.Groups[1].Value)
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .ToList();

        _out.WriteLine($"  JSON keys containing 'size': " +
                       (keys.Count > 0 ? string.Join(", ", keys) : "(none)"));

        _out.WriteLine(string.Empty);
    }

    [Fact]
    public async Task EachStoreShowsHowItCarriesSizes()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        await ProbeAsync(net, "hbx", HbxProduct);
        await ProbeAsync(net, "popmart", PopMartProduct);

        Assert.True(true);
    }
}
