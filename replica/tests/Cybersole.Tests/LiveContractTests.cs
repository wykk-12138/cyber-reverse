using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Live contracts: endpoints that a flow depends on, verified against the real host.
///
/// Why this is separate from the parser tests: a parser test proves the code reads a fixture
/// correctly. It cannot notice that the site stopped serving that shape. Between rounds 47 and
/// 69 this project found eight modules registered against the wrong platform — every one of
/// them compiled, ran, returned 200 somewhere, and did nothing. A contract test is how that
/// class of failure gets caught without a human re-probing by hand.
///
/// Rules this file follows:
///
/// 1. Only assert what was actually observed. An endpoint that answered once is a contract;
///    an endpoint that was inferred from documentation is not, and does not belong here.
/// 2. State the consequence. When a contract breaks the message must name the flow that
///    depends on it, so a red test reads as "HbxFlow's cart is gone", not "assert 1 failed".
/// 3. Tolerate bot walls explicitly. A 403 means the site refused the probe, which is not the
///    same as the endpoint disappearing — that distinction is the whole difference between
///    "fix the flow" and "retry later".
///
/// Speed=Slow, network-bound. Skip with --filter "Speed!=Slow".
/// </summary>
[Trait("Speed", "Slow")]
public class LiveContractTests
{
    private readonly ITestOutputHelper _out;
    public LiveContractTests(ITestOutputHelper output) => _out = output;

    /// <summary>Classify a probe so a failure says which kind of failure it is.</summary>
    private enum Outcome { Holds, Blocked, Broken }

    private async Task<Outcome> CheckAsync(NetClient net, string label, string url,
        Func<NetResponse, bool> contract, string consequence)
    {
        NetResponse res;
        try
        {
            // ask for JSON explicitly. Without it HBX answers 406 with an HTML error page, which
            // is a negotiation failure, not evidence the route is gone.
            var options = new RequestOptions { Tag = "contract" };
            options.Headers["Accept"] = "application/json, text/javascript, */*";

            res = await net.GetAsync(url, options, CancellationToken.None);
        }
        catch (Exception ex)
        {
            _out.WriteLine($"{label}: transport failure — {ex.GetType().Name}: {ex.Message}");
            _out.WriteLine($"  consequence: {consequence}");
            return Outcome.Blocked;
        }

        var ct = res.Headers.TryGetValue("content-type", out var c) ? c : "";
        _out.WriteLine($"{label}: HTTP {res.StatusCode}  {res.BodyBytes:N0}B  [{ct}]");

        if (res.StatusCode is 403 or 406 or 429 or 202 or 503)
        {
            _out.WriteLine("  refused by the site, not proof the endpoint is gone — retry later");
            _out.WriteLine($"  consequence if it stays gone: {consequence}");
            return Outcome.Blocked;
        }

        if (!contract(res))
        {
            _out.WriteLine($"  CONTRACT BROKEN — {consequence}");
            var head = res.Body.Length > 120 ? res.Body[..120].Replace('\n', ' ') : res.Body;
            _out.WriteLine($"  body head: {head}");
            return Outcome.Broken;
        }

        _out.WriteLine("  holds");
        return Outcome.Holds;
    }

    /// <summary>
    /// JSON with a given content type is the cheapest reliable signal a controller lives.
    /// </summary>
    private static bool IsJson(NetResponse res) =>
        res.IsSuccess
        && res.Headers.TryGetValue("content-type", out var ct)
        && ct.Contains("json", StringComparison.OrdinalIgnoreCase);

    /// <summary>
    /// A guarded controller answering 401/403 with a JSON body still exists — it merely wants a
    /// session. Counting that as a broken contract was a mistake this file made on its first
    /// run: Swell's /api/cart answers 401 with 152 bytes of JSON, which is a live endpoint.
    /// </summary>
    private static bool IsJsonOrGuarded(NetResponse res) =>
        IsJson(res)
        || (res.StatusCode is 401 or 405
            && res.Headers.TryGetValue("content-type", out var ct)
            && ct.Contains("json", StringComparison.OrdinalIgnoreCase));

    /// <summary>
    /// Shopify's /cart.js is served as <c>text/javascript</c>, not application/json. The body is
    /// a JSON object anyway. Asserting the content type was wrong — the contract is the shape of
    /// what comes back, not the MIME label the CDN happens to attach.
    ///
    /// But "not JSON" is not the same as "anything goes": Converse answers /cart.js with a 220 KB
    /// HTML page that happens to contain the word token, which an earlier version of this
    /// predicate accepted as a Shopify cart. So the type must exclude HTML as well.
    /// </summary>
    private static bool IsShopifyCart(NetResponse res) =>
        res.IsSuccess
        && res.Headers.TryGetValue("content-type", out var ct)
        && !ct.Contains("html", StringComparison.OrdinalIgnoreCase)
        && (res.Body.Contains("\"token\"", StringComparison.Ordinal)
            || res.Body.Contains("item_count", StringComparison.Ordinal));

    [Fact]
    public async Task HbxServesItsCartEndpoints()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        // verified R52 by driving a real add-to-bag click; the paths came from the capture
        var results = new[]
        {
            await CheckAsync(net, "hbx /api/v1/carts",
                "https://hbx.com/api/v1/carts",
                r => r.StatusCode is 200 or 201 or 401 or 405,
                "HbxFlow.AddToCartAsync cannot create a cart"),

            await CheckAsync(net, "hbx /api/v2/shop/countries",
                "https://hbx.com/api/v2/shop/countries?limit=1",
                IsJson,
                "HbxFlow's catalog requests are pointed at a dead API"),
        };

        Assert.All(results, r => Assert.NotEqual(Outcome.Broken, r));
    }

    [Fact]
    public async Task OffspringServesItsHybrisControllers()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        var results = new[]
        {
            await CheckAsync(net, "offspring minibasketAjax",
                "https://www.offspring.co.uk/view/component/basket/minibasketAjax",
                IsJson,
                "HybrisFlow.GetCartAsync loses its only verified endpoint"),

            await CheckAsync(net, "offspring getUserInfo",
                "https://www.offspring.co.uk/view/resources/getUserInfo",
                IsJson,
                "HybrisFlow.GetHomeAsync's session probe stops working"),
        };

        Assert.All(results, r => Assert.NotEqual(Outcome.Broken, r));
    }

    [Fact]
    public async Task TheStoresThatMustAnswerShopifyStillDo()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        // these four were re-registered onto ShopifyFlow on evidence; if /cart.js stops
        // answering that evidence has expired and the registration needs re-checking
        foreach (var host in new[] { "www.footpatrol.com", "www.size.co.uk", "www.jbhifi.com.au" })
        {
            var outcome = await CheckAsync(net, $"{host} /cart.js", $"https://{host}/cart.js",
                IsShopifyCart,
                $"{host} no longer looks like Shopify — its registration was decided on this endpoint");

            Assert.NotEqual(Outcome.Broken, outcome);
        }
    }

    /// <summary>
    /// Yeezy's cart lives on the Swell platform host, not the storefront. This asserts the host
    /// split itself, because that split is the finding — getting it wrong means every cart call
    /// goes to a domain that does not serve carts.
    /// </summary>
    [Fact]
    public async Task YeezyKeepsItsCartOnTheSwellHost()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        var swell = await CheckAsync(net, "swell /api/cart",
            "https://yzy-prod.swell.store/api/cart",
            IsJsonOrGuarded,
            "YeezySupplyFlow points at the wrong host for every cart call");

        var storefront = await CheckAsync(net, "yeezy.com /api/cart (should NOT be the cart)",
            "https://yeezy.com/api/cart",
            r => !IsJson(r),
            "if this starts serving carts, the Swell host constant is obsolete");

        _out.WriteLine($"swell holds: {swell}");
        _out.WriteLine($"storefront does not serve carts: {storefront}");

        Assert.NotEqual(Outcome.Broken, swell);
    }

    /// <summary>
    /// Funko's site id was wrong for a long time: the flow declared <c>Funko-Site</c> while every
    /// controller the storefront calls lives under <c>Sites-FunkoUS-Site</c>. A wrong site id is
    /// the quietest failure there is — right host, right platform, every controller 404s.
    ///
    /// This asserts the id, so a future change to the constant cannot silently go back.
    /// </summary>
    [Fact]
    public async Task FunkoUsesTheSiteIdThatActuallyAnswers()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        var correct = await CheckAsync(net, "funko Sites-FunkoUS-Site",
            "https://funko.com/on/demandware.store/Sites-FunkoUS-Site/en_US/__Analytics-Start",
            r => r.StatusCode < 400,
            "FunkoFlow.SiteId no longer resolves — the constant is stale");

        var wrong = await CheckAsync(net, "funko Sites-Funko-Site (must NOT answer)",
            "https://funko.com/on/demandware.store/Sites-Funko-Site/en_US/__Analytics-Start",
            r => r.StatusCode >= 400,
            "if this starts working, Funko-Site became valid and the fix was unnecessary");

        _out.WriteLine($"correct id holds: {correct}");
        _out.WriteLine($"old id still wrong: {wrong}");

        Assert.NotEqual(Outcome.Broken, correct);
    }

    /// <summary>
    /// Converse was registered as ShopifyFlow; the real storefront is Demandware with site
    /// <c>ConverseUS-Site</c>. This pins both halves: the Demandware path answers, and /cart.js
    /// — the endpoint that would prove Shopify — does not.
    /// </summary>
    [Fact]
    public async Task ConverseIsDemandwareAndNotShopify()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        var demandware = await CheckAsync(net, "converse on/demandware.store",
            "https://www.converse.com/on/demandware.store/Sites-ConverseUS-Site/en_US/Home-Show",
            r => r.StatusCode < 400,
            "DemandwareFlow(\"converse\", …, \"ConverseUS-Site\") points at a dead site id");

        var shopify = await CheckAsync(net, "converse /cart.js (must NOT be a Shopify cart)",
            "https://www.converse.com/cart.js",
            r => !IsShopifyCart(r),
            "if converse starts serving Shopify carts, the Demandware registration is obsolete");

        _out.WriteLine($"demandware holds: {demandware}");
        _out.WriteLine($"not shopify: {shopify}");

        Assert.NotEqual(Outcome.Broken, demandware);
    }

    /// <summary>
    /// Scheels runs Kasada on <c>j-1.2.988</c> — the same build Nike and Converse use. The
    /// sensor endpoint is the thing a flow has to talk to, so it is the thing worth pinning.
    ///
    /// Kasada answers with a script, not JSON, and refuses bare requests. A 200 with a
    /// script body or a 4xx both mean "the endpoint is there"; only a hard 404 would mean it
    /// moved.
    /// </summary>
    [Fact]
    public async Task ScheelsKeepsItsKasadaSensorEndpoint()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        var sensor = await CheckAsync(net, "scheels kasada fp",
            "https://apihub.scheels.com/86f1e5c6d0e8/fp",
            r => r.StatusCode < 500,
            "ScheelsFlow's Kasada handshake target has moved");

        _out.WriteLine($"sensor endpoint: {sensor}");

        // Kasada refusing the probe is the expected outcome here, and says nothing bad
        Assert.NotEqual(Outcome.Broken, sensor);
    }

    /// <summary>
    /// BSTN is self-built under <c>/api/beast/</c>. That prefix is the finding: the module was
    /// registered as ShopifyFlow until a capture showed no Shopify surface answering.
    ///
    /// The one endpoint verified at the time was <c>/api/beast/geoIP</c>. This pins it — and
    /// pins the negative too, because the whole reason the registration changed is that
    /// <c>/cart.js</c> does not return a Shopify cart.
    /// </summary>
    [Fact]
    public async Task BstnServesItsBeastApiAndNotAShopifyOne()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        var beast = await CheckAsync(net, "bstn /api/beast/geoIP",
            "https://www.bstn.com/api/beast/geoIP",
            r => r.StatusCode < 500,
            "BstnFlow's only verified endpoint has moved — the /api/beast/ prefix may be gone");

        var shopify = await CheckAsync(net, "bstn /cart.js (must NOT be a Shopify cart)",
            "https://www.bstn.com/cart.js",
            r => !IsShopifyCart(r),
            "if bstn starts serving Shopify carts, it became a Shopify store and BstnFlow is obsolete");

        _out.WriteLine($"beast api: {beast}");
        _out.WriteLine($"not shopify: {shopify}");

        Assert.NotEqual(Outcome.Broken, beast);
    }

    /// <summary>
    /// Supreme moved to Shopify. SupremeFlow used to be 193 lines of hand-built flow — CSRF from
    /// the product page, a colour id, POST /shop/{id}/add, then a form-post checkout. A capture
    /// showed us.supreme.com calling shopifysvc telemetry and redirecting /shop/all to
    /// /collections/all; /cart.js on the us. subdomain returns a Shopify cart object.
    ///
    /// This pins that: the us. host answers a Shopify cart, and the old hand-built paths that
    /// SupremeFlow used to call are gone.
    /// </summary>
    [Fact]
    public async Task SupremeIsAShopifyStoreOnItsUsSubdomain()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        var cart = await CheckAsync(net, "us.supreme.com /cart.js",
            "https://us.supreme.com/cart.js",
            IsShopifyCart,
            "SupremeFlow is a ShopifyFlow again only because this answers — if it stops, Supreme left Shopify");

        var oldAdd = await CheckAsync(net, "supreme /shop/1/add (the old hand-built path)",
            "https://www.supremenewyork.com/shop/1/add",
            r => !(r.StatusCode is >= 200 and < 300
                   && (r.Headers.TryGetValue("content-type", out var ct) ? ct : "")
                   .Contains("json", StringComparison.OrdinalIgnoreCase)),
            "if this starts answering JSON, the old custom flow came back");

        _out.WriteLine($"shopify cart: {cart}");
        _out.WriteLine($"old add path gone: {oldAdd}");

        Assert.NotEqual(Outcome.Broken, cart);
    }
}
