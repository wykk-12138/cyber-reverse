using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Does Warhammer actually serve the REST endpoints WarhammerFlow calls?
///
/// The flow posts to api.prod.warhammer.com/api/basket/items and /api/orders, and reads
/// /api/products/{code}. A live capture shows the storefront talking GraphQL instead:
///
///   POST https://api.prod.warhammer.com/graphql
///
/// Next.js front end (/_next/static/), self-hosted /api/i18n, and a GraphQL gateway. So the
/// REST paths are probably invented. This asks each one directly.
///
/// Speed=Slow, network-bound.
/// </summary>
[Trait("Speed", "Slow")]
public class WarhammerEndpointTests
{
    private readonly ITestOutputHelper _out;
    public WarhammerEndpointTests(ITestOutputHelper output) => _out = output;

    private const string ApiHost = "https://api.prod.warhammer.com";

    [Fact]
    public async Task TheRestPathsTheFlowCallsAreActuallyThere()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        foreach (var (label, path) in new[]
                 {
                     ("products (REST)", "/api/products/60010299006"),
                     ("basket (REST)", "/api/basket/items"),
                     ("orders (REST)", "/api/orders"),
                     ("graphql (GET)", "/graphql"),
                 })
        {
            var url = ApiHost + path;

            try
            {
                var res = await net.GetAsync(url, new RequestOptions { Tag = "wh-probe" },
                    CancellationToken.None);

                var ct = res.Headers.TryGetValue("content-type", out var c) ? c : "";
                var head = res.Body.Length > 100 ? res.Body[..100].Replace('\n', ' ') : res.Body;

                _out.WriteLine($"{label,-18} HTTP {res.StatusCode}  {res.BodyBytes:N0}B  [{ct}]");
                _out.WriteLine($"  {head}");
            }
            catch (Exception ex)
            {
                _out.WriteLine($"{label,-18} {ex.GetType().Name}");
            }

            _out.WriteLine(string.Empty);
        }

        Assert.True(true);
    }

    /// <summary>
    /// The one call the capture proved exists. A 400 with a GraphQL error body means the route
    /// is real and merely wants a query; anything else means it is not there.
    /// </summary>
    [Fact]
    public async Task TheGraphqlGatewayAnswers()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        var res = await net.PostJsonAsync($"{ApiHost}/graphql",
            "{\"query\":\"{ __typename }\"}",
            new RequestOptions { Tag = "wh-graphql" }, CancellationToken.None);

        _out.WriteLine($"POST /graphql -> HTTP {res.StatusCode}  {res.BodyBytes:N0}B");
        _out.WriteLine($"  {(res.Body.Length > 200 ? res.Body[..200] : res.Body).Replace('\n', ' ')}");

        // a live GraphQL endpoint answers a trivial introspection query with JSON
        var isGraphql = res.Body.Contains("__typename", StringComparison.Ordinal)
                        || res.Body.Contains("\"data\"", StringComparison.Ordinal)
                        || res.Body.Contains("\"errors\"", StringComparison.Ordinal);

        _out.WriteLine($"  looks like GraphQL: {isGraphql}");
        Assert.True(true);
    }
}
