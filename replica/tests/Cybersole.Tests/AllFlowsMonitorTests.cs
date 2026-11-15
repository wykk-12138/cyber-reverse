using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Http.Stores;
using Cybersole.Services;
using Cybersole.Stores.Modules;
using Cybersole.Tests.Support;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R24: broaden functional coverage beyond Shopify and Nike.
///
/// Every registered flow gets driven through a monitor pass against a mock that answers like a
/// generic storefront. The point is not that each flow succeeds — some legitimately need a
/// signature or an account — but that each one parses, records its steps, and fails for a
/// reason it can name.
/// </summary>
[Trait("Speed", "Slow")]
public class AllFlowsMonitorTests
{
    private readonly ITestOutputHelper _out;
    public AllFlowsMonitorTests(ITestOutputHelper output) => _out = output;

    /// <summary>A response shape that satisfies most product parsers at once.</summary>
    private const string UniversalProduct = """
        <html><head><title>Test Product</title>
        <meta property="og:image" content="https://cdn.example.com/a.jpg">
        <script type="application/ld+json">
        {"@type":"Product","name":"Test Product","offers":{"price":"150.00","availability":"InStock"}}
        </script></head>
        <body>
        <input type="hidden" name="authenticity_token" value="csrf-abc" />
        <script id="__NEXT_DATA__" type="application/json">
        {"props":{"pageProps":{"product":{"id":11,"title":"Test Product","handle":"test-product",
          "variants":[{"id":101,"title":"10","public_title":"10","price":"150.00","available":true}]}}}}
        </script>
        <script>Shopify.currency = {"active":"USD"};</script>
        </body></html>
        """;

    // Carries every key the parsers look for, so a failure here means a parser bug rather
    // than the mock being too thin.
    private const string UniversalJson = """
        {"id":11,"productId":11,"sku":"TEST-SKU-1","skuId":101,"variantId":101,
         "title":"Test Product","name":"Test Product","handle":"test-product",
         "price":"150.00","total_price":15000,
         "size":"10","sizeName":"10",
         "raffleOpen":true,"inStock":true,"available":true,
         "variants":[{"id":101,"sku":"TEST-SKU-1","skuId":101,"variantId":101,
           "title":"10","name":"10","public_title":"10","size":"10",
           "price":"150.00","available":true,"inventory_quantity":5}],
         "items":[{"id":101,"sku":"TEST-SKU-1","quantity":1}]}
        """;

    private static TinyServer BuildMock() => new((req, _) =>
    {
        var path = req.Url!.AbsolutePath;

        if (path.EndsWith(".json", StringComparison.OrdinalIgnoreCase) ||
            path.Contains("/api/", StringComparison.OrdinalIgnoreCase) ||
            path.Contains("graphql", StringComparison.OrdinalIgnoreCase))
            return (200, UniversalJson);

        if (path.EndsWith(".js", StringComparison.OrdinalIgnoreCase))
            return (200, UniversalJson);

        return (200, UniversalProduct);
    });

    private static Product TestProduct(string baseUrl, string path) => new()
    {
        Name = "Test Product",
        Url = baseUrl + path,
        Sizes = new List<string> { "10" },
    };

    private static IEnumerable<(string Id, IStoreModule Module)> AllModules()
        => StoreModuleCatalog.CreateAll()
            .Select(m => (m.Id, m))
            .OrderBy(x => x.Id, StringComparer.Ordinal);

    [Fact]
    public async Task EveryFlowSurvivesAMonitorPassAgainstAGenericStore()
    {
        using var services = TestServices.Create();
        using var store = BuildMock();

        var results = new List<(string Id, MonitorStatus Status, int Steps, string? Error)>();

        foreach (var (id, module) in AllModules())
        {
            var path = id is "nike" ? "/launch/t/test-product" : "/products/test-product";

            var monitor = new MonitorContext
            {
                Http = services.Http,
                Url = store.BaseUrl + path,
                Product = TestProduct(store.BaseUrl, path),
                TimeoutSeconds = 5,
            };

            MonitorResult result;
            try
            {
                result = await module.MonitorAsync(monitor, default);
            }
            catch (Exception ex)
            {
                result = new MonitorResult
                {
                    Status = MonitorStatus.Error,
                    Error = "threw: " + ex.Message,
                };
            }

            results.Add((id, result.Status, result.Sizes.Count, result.Error));
        }

        foreach (var r in results)
            _out.WriteLine($"{r.Id,-22} {r.Status,-12} sizes={r.Steps} {r.Error}");

        var available = results.Where(r => r.Status == MonitorStatus.Available).ToList();
        _out.WriteLine($"available: {available.Count} / {results.Count}");

        // Nothing may blow up.
        Assert.DoesNotContain(results, r => r.Error?.StartsWith("threw:", StringComparison.Ordinal) == true);

        // A generic storefront should satisfy a healthy share of the catalogue.
        Assert.True(available.Count >= 10,
            $"only {available.Count} of {results.Count} flows could read a generic store; " +
            "the parsers are narrower than the stores they target");
    }

    [Fact]
    public void TheMockAnswersLikeARealStore()
    {
        // guard the guard: if the mock itself is broken, every failure above is meaningless
        using var services = TestServices.Create();
        using var store = BuildMock();

        var res = services.Http.GetAsync(store.BaseUrl + "/products/test-product",
                new RequestOptions { Timeout = TimeSpan.FromSeconds(5), Tag = "probe" })
            .GetAwaiter().GetResult();

        Assert.Equal(200, res.StatusCode);
        Assert.Contains("Test Product", res.Body);
    }
}



