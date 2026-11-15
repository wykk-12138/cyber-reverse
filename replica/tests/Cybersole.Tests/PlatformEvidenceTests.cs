using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// What platform are the MagentoFlow-wrapped brands actually on?
///
/// The REST probe found no Magento surface on any of them. Two of them — footpatrol.com and
/// size.co.uk — answered <c>/customer/section/load/?sections=cart</c> with:
///
///   {"cart":"&lt;section id=\"shopify-section-cart\" class=\"shopify-section ..."}
///
/// <c>shopify-section-cart</c> is Shopify's own section naming, embedded in a Magento-shaped
/// JSON envelope. That combination is unusual enough to pin down rather than guess at, so this
/// records the direct evidence per host: what /cart.js answers, and what the storefront's own
/// HTML says about the platform.
///
/// Speed=Slow, network-bound.
/// </summary>
[Trait("Speed", "Slow")]
public class PlatformEvidenceTests
{
    private readonly ITestOutputHelper _out;
    public PlatformEvidenceTests(ITestOutputHelper output) => _out = output;

    private static readonly string[] Hosts =
    {
        "footpatrol.com", "size.co.uk", "offspring.co.uk", "jdsports.co.uk",
    };

    /// <summary>Markers each platform puts in its own HTML.</summary>
    private static readonly (string Platform, string Marker, bool NeedsJson)[] Markers =
    {
        ("Shopify", "cdn.shopify.com", false),
        ("Shopify", "shopify-section", false),
        ("Shopify", "Shopify.theme", false),
        ("Magento", "Magento_", false),
        ("Magento", "mage/cookies", false),
        ("Magento", "static/version", false),
        ("Salesforce", "demandware", false),
        ("Next.js", "__NEXT_DATA__", false),
    };

    [Fact]
    public async Task EachMagentoWrappedHostShowsItsRealPlatform()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        foreach (var host in Hosts)
        {
            _out.WriteLine($"=== {host} ===");

            // 1. the storefront page itself
            try
            {
                var home = await net.GetAsync($"https://{host}/",
                    new RequestOptions { Tag = "platform-home" }, CancellationToken.None);

                _out.WriteLine($"  home      HTTP {home.StatusCode}  {home.BodyBytes:N0}B");

                if (home.IsSuccess && home.BodyBytes > 5000)
                {
                    var found = Markers
                        .Where(m => home.Body.Contains(m.Marker, StringComparison.OrdinalIgnoreCase))
                        .Select(m => m.Platform)
                        .Distinct()
                        .ToList();

                    _out.WriteLine($"  markers   {(found.Count > 0 ? string.Join(", ", found) : "(none of the known ones)")}");

                    foreach (var m in Markers.Where(m =>
                                 home.Body.Contains(m.Marker, StringComparison.OrdinalIgnoreCase)))
                        _out.WriteLine($"    hit {m.Platform,-12} {m.Marker}");
                }
            }
            catch (Exception ex)
            {
                _out.WriteLine($"  home      {ex.GetType().Name}");
            }

            // 2. the two canonical cart endpoints, one per platform
            foreach (var (label, path, shape) in new[]
                     {
                         ("shopify", "/cart.js", "\"items\""),
                         ("magento", "/customer/section/load/?sections=cart", "\"cart\""),
                     })
            {
                try
                {
                    var res = await net.GetAsync($"https://{host}{path}",
                        new RequestOptions { Tag = "platform-cart" }, CancellationToken.None);

                    var ct = res.Headers.TryGetValue("content-type", out var c) ? c : "";
                    var hit = res.StatusCode == 200 && res.Body.Contains(shape, StringComparison.Ordinal);

                    var head = res.Body.Length > 80 ? res.Body[..80].Replace('\n', ' ') : res.Body;
                    _out.WriteLine($"  {label,-8}  {(hit ? "HIT " : "miss")}  HTTP {res.StatusCode}  " +
                                   $"{res.BodyBytes:N0}B  [{ct}]  {head}");
                }
                catch (Exception ex)
                {
                    _out.WriteLine($"  {label,-8}  error  {ex.GetType().Name}");
                }
            }

            _out.WriteLine(string.Empty);
        }

        Assert.True(true);
    }
}
