using System.Linq;
using System.Threading.Tasks;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 141: the six walls audited at once, and Kasada wired the way Cloudflare was.
///
/// <para>
/// The audit's value is the third column: detection and cookie storage were both cheap and both
/// present, and before R140 the call between them was missing for <b>every</b> vendor. Two are wired
/// now, and the four that are not are recorded with the kind of gap each one is — a host without a
/// protocol, no cookie at all, or a queue that should be waited on rather than solved.
/// </para>
/// </summary>
public sealed class VendorWiringTests
{
    private readonly ITestOutputHelper _out;

    public VendorWiringTests(ITestOutputHelper output) => _out = output;

    private static FlowContext Context(string vendor)
    {
        var context = new FlowContext { Url = "https://example.test/", Http = null! };
        context.Session.Vars["antibot"] = vendor;
        return context;
    }

    /// <summary>Six vendors, and the two wired ones are the two this session built.</summary>
    [Fact]
    public void TwoOfSixAreWired()
    {
        Assert.Equal(6, VendorWiring.Rows.Count);
        Assert.Equal(new[] { "cloudflare", "kasada" }, VendorWiring.Wired);

        foreach (var row in VendorWiring.Rows)
            _out.WriteLine($"{row.Vendor,-12} {row.State,-20} {row.Note}");
    }

    /// <summary>The four gaps are four different kinds of gap.</summary>
    [Fact]
    public void TheGapsAreClassified()
    {
        Assert.Equal(new[] { "imperva", "datadome", "perimeterx", "queue-it" }, VendorWiring.Gaps);

        Assert.Equal(VendorWiring.State.HostWithoutProtocol,
            VendorWiring.For("datadome")!.State);
        Assert.Equal(VendorWiring.State.DetectedOnly, VendorWiring.For("imperva")!.State);
        Assert.Equal(VendorWiring.State.DetectedOnly, VendorWiring.For("perimeterx")!.State);
        Assert.Equal(VendorWiring.State.NotAChallenge, VendorWiring.For("queue-it")!.State);

        // the kinds differ in what would unblock them
        Assert.NotEqual(VendorWiring.For("datadome")!.State, VendorWiring.For("queue-it")!.State);
    }

    /// <summary>The audit's cookie column agrees with the protocol table.</summary>
    [Fact]
    public void TheCookieColumnAgreesWithTheProtocolTable()
    {
        foreach (var row in VendorWiring.Rows.Where(r => r.Cookie is not null))
        {
            var cookies = AntiBotProtocol.CookiesFor(row.Vendor);
            if (cookies is null)
            {
                // queue-it keeps its cookie in its own list, not the per-vendor table
                Assert.Equal("queue-it", row.Vendor);
                Assert.Contains(row.Cookie!, AntiBotProtocol.QueueIt);
                continue;
            }

            Assert.Contains(row.Cookie!, cookies);
        }

        // and the two vendors with no cookie named stay that way
        Assert.Null(AntiBotProtocol.CookiesFor("PerimeterX"));
        Assert.Null(AntiBotProtocol.CookiesFor("Imperva"));
    }

    /// <summary>A Kasada wall now gets a token, a mode, and a status.</summary>
    [Fact]
    public async Task AKasadaTokenIsStoredWithItsRoad()
    {
        var c = Context("kasada");

        var api = new ApiKasadaSolver("https://solver.test/kasada",
            (_, _, _) => Task.FromResult<string?>("kasada-token"));
        var runner = new KasadaStrategyRunner(new IKasadaSolver[]
        {
            api,
            new NamedFallbackSolver(KasadaStrategy.Mode.Fallback),
        });

        var outcome = await KasadaClearance.ApplyAsync(c, runner, "https://example.test/");

        Assert.True(outcome.Ok);
        Assert.Equal("kasada-token", KasadaClearance.Token(c.Session));
        Assert.Equal(KasadaStrategy.Mode.Api, KasadaClearance.Mode(c.Session));
        Assert.NotNull(KasadaClearance.Status(c.Session));

        _out.WriteLine(KasadaClearance.Status(c.Session)!);
    }

    /// <summary>A give-up keeps every road's status and writes no token.</summary>
    [Fact]
    public async Task AGiveUpWritesNoToken()
    {
        var c = Context("kasada");
        var runner = new KasadaStrategyRunner(new IKasadaSolver[]
        {
            new ApiKasadaSolver(),
            new NamedFallbackSolver(KasadaStrategy.Mode.Fallback),
        });

        await KasadaClearance.ApplyAsync(c, runner, "https://example.test/");

        Assert.Null(KasadaClearance.Token(c.Session));
        Assert.Contains(KasadaStrategyRunner.GaveUpStatus, KasadaClearance.Status(c.Session)!);
    }

    /// <summary>Another vendor's wall is left alone — the same rule as Cloudflare's.</summary>
    [Fact]
    public async Task AnotherVendorsWallIsLeftAlone()
    {
        foreach (var vendor in new[] { "cloudflare", "datadome", "none" })
        {
            var c = Context(vendor);
            var runner = new KasadaStrategyRunner(new IKasadaSolver[]
            {
                new ApiKasadaSolver("https://x.test", (_, _, _) => Task.FromResult<string?>("nope")),
            });

            await KasadaClearance.ApplyAsync(c, runner, "https://example.test/");

            Assert.Null(KasadaClearance.Token(c.Session));
        }

        _out.WriteLine("only the Kasada wall is this helper's business");
    }

    /// <summary>The audit states the rule the last three rounds kept rediscovering.</summary>
    [Fact]
    public void TheAuditStatesItsRule()
    {
        Assert.Contains("detection and storage", VendorWiring.AuditRule);
        Assert.Contains("the call between them is the work", VendorWiring.AuditRule);
        _out.WriteLine(VendorWiring.AuditRule);
    }
}
