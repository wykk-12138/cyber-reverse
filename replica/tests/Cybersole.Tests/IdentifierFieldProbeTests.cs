using System.Text.RegularExpressions;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Shows which identifier fields a product page actually carries.
///
/// The generic probe reports <c>skuish</c> as a miss on HBX and PopMart. That could mean either
/// "these stores have no SKU" (unlikely for a shop) or "the field is named something the
/// pattern does not cover". This prints the real field names with values so the difference can
/// be told apart instead of guessed.
///
/// Speed=Slow, network-bound.
/// </summary>
[Trait("Speed", "Slow")]
public class IdentifierFieldProbeTests
{
    private readonly ITestOutputHelper _out;
    public IdentifierFieldProbeTests(ITestOutputHelper output) => _out = output;

    private static readonly (string Module, string Url)[] Targets =
    {
        ("hbx", "https://hbx.com/men/brands/veja/volley-leather-white-green"),
        ("popmart", "https://www.popmart.com/us/products/4205/dimoo-becoming-a-tree-figure"),
    };

    /// <summary>
    /// Any field whose name looks like an identifier. Deliberately loose: the first version
    /// required a sku/variant-ish substring and matched nothing at all, which says the field
    /// naming on these pages is not what the flows assume.
    /// </summary>
    private static readonly Regex IdField = new(
        @"""([\w$]*(?:_id|Id|ID|id|sku|Sku|SKU|code|Code|ean|upc)[\w$]*)""\s*:\s*""?([\w\-.]{1,48})""?",
        RegexOptions.IgnoreCase);

    [Fact]
    public async Task EveryIdentifierFieldOnThePageIsListed()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        foreach (var (module, url) in Targets)
        {
            _out.WriteLine($"=== {module} ===");

            NetResponse res;
            try
            {
                res = await net.GetAsync(url, new RequestOptions { Tag = "id-probe" },
                    CancellationToken.None);
            }
            catch (Exception ex)
            {
                _out.WriteLine($"  unreachable: {ex.GetType().Name}");
                continue;
            }

            _out.WriteLine($"  HTTP {res.StatusCode}  {res.BodyBytes:N0} bytes");
            if (!res.IsSuccess || res.BodyBytes < 5000)
            {
                _out.WriteLine("  challenge page — cannot inspect fields");
                _out.WriteLine(string.Empty);
                continue;
            }

            var seen = new Dictionary<string, List<string>>(StringComparer.OrdinalIgnoreCase);

            foreach (Match m in IdField.Matches(res.Body))
            {
                var name = m.Groups[1].Value;
                var value = m.Groups[2].Value;

                if (!seen.TryGetValue(name, out var list))
                    seen[name] = list = new List<string>();

                if (list.Count < 3 && !list.Contains(value)) list.Add(value);
            }

            if (seen.Count == 0)
            {
                _out.WriteLine("  no identifier-shaped field at all");
            }
            else
            {
                foreach (var (name, values) in seen.OrderByDescending(kv => kv.Value.Count))
                    _out.WriteLine($"  {name,-24} {string.Join(", ", values)}");
            }

            // what the module's own matcher would pick, for comparison
            if (module == "popmart")
            {
                var skuish = Regex.Match(res.Body,
                    @"""(?:sku|skuId|variantId|productId)""\s*:\s*""?([A-Za-z0-9_\-]+)""?");
                _out.WriteLine($"  module skuish match -> " +
                               (skuish.Success ? skuish.Groups[1].Value : "(none)"));
            }

            _out.WriteLine(string.Empty);
        }

        Assert.True(true);
    }
}
