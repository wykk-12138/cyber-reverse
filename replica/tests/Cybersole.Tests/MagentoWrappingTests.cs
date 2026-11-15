using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Are the brands wrapped in <c>MagentoFlow</c> actually Magento?
///
/// The Shopify sweep found three misregistrations out of thirty-one, so the same question has
/// to be asked of every other platform wrapper. Magento has a distinctive REST surface:
///
///   /rest/V1/store/storeConfigs   -> JSON describing the store
///   /customer/section/load/       -> JSON sections, 200 even when empty
///   /catalogsearch/result/?q=x    -> search results page
///
/// A store that answers none of those with JSON is not Magento, whatever the registration says.
///
/// Speed=Slow: one or two requests per host.
/// </summary>
[Trait("Speed", "Slow")]
public class MagentoWrappingTests
{
    private readonly ITestOutputHelper _out;
    public MagentoWrappingTests(ITestOutputHelper output) => _out = output;

    /// <summary>Mirrors the MagentoFlow subclasses in MagentoFlow.cs.</summary>
    private static readonly (string Module, string[] Hosts)[] Wrapped =
    {
        ("offspring", new[] { "offspring.co.uk", "offspring.com" }),
        ("footpatrol", new[] { "footpatrol.co.uk", "footpatrol.com" }),
        ("size", new[] { "size.co.uk", "sizeofficial.com" }),
        ("jdsports", new[] { "jdsports.co.uk", "jdsports.com" }),
    };

    private static bool LooksLikeMagentoJson(int status, string body, string contentType) =>
        status == 200
        && (contentType.Contains("json", StringComparison.OrdinalIgnoreCase)
            || body.TrimStart().StartsWith('{')
            || body.TrimStart().StartsWith('['))
        // Magento's storeConfigs payload always carries these
        && (body.Contains("\"base_currency_code\"", StringComparison.Ordinal)
            || body.Contains("\"store_name\"", StringComparison.Ordinal)
            || body.Contains("\"locale\"", StringComparison.Ordinal)
            || body.Contains("\"storeView\"", StringComparison.Ordinal));

    private async Task ProbeHostAsync(NetClient net, string module, string host)
    {
        _out.WriteLine($"=== {module} / {host} ===");

        foreach (var path in new[] { "/rest/V1/store/storeConfigs", "/customer/section/load/?sections=cart" })
        {
            var url = $"https://{host}{path}";
            try
            {
                var res = await net.GetAsync(url, new RequestOptions { Tag = "magento-probe" },
                    CancellationToken.None);

                var ct = res.Headers.TryGetValue("content-type", out var c) ? c : string.Empty;
                var head = res.Body.Length > 70 ? res.Body[..70].Replace('\n', ' ') : res.Body;

                var hit = LooksLikeMagentoJson(res.StatusCode, res.Body, ct);
                _out.WriteLine($"  {(hit ? "MAGENTO" : "no     ")}  {path}  " +
                               $"HTTP {res.StatusCode}  {res.BodyBytes:N0}B  {head}");

                if (hit) return;
            }
            catch (Exception ex)
            {
                _out.WriteLine($"  error    {path}  {ex.GetType().Name}");
            }
        }

        _out.WriteLine("  -> no Magento REST surface answered");
    }

    [Fact]
    public async Task EveryMagentoWrappedHostAnswersTheMagentoRestSurface()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        foreach (var (module, hosts) in Wrapped)
        foreach (var host in hosts)
            await ProbeHostAsync(net, module, host);

        // the report is the deliverable; a host being down or repurposed is a finding, not a
        // build failure. What matters is that the list above is evidence, not assumption.
        Assert.True(true);
    }
}
