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
    public void ThreeOfSixAreWired()
    {
        Assert.Equal(6, VendorWiring.Rows.Count);
        Assert.Equal(new[] { "cloudflare", "kasada", "datadome" }, VendorWiring.Wired);

        foreach (var row in VendorWiring.Rows)
            _out.WriteLine($"{row.Vendor,-12} {row.State,-20} {row.Note}");
    }

    /// <summary>The four gaps are four different kinds of gap.</summary>
    [Fact]
    public void TheGapsAreClassified()
    {
        Assert.Equal(new[] { "imperva", "perimeterx", "queue-it" }, VendorWiring.Gaps);

        // R995: this row used to assert HostWithoutProtocol, which said the protocol does not exist. R141 had already
        // established the opposite -- SolveBotD is named by a method in the original -- so the assertion was holding a
        // conclusion the same repository had corrected. What differs now is the attribution: the protocol exists in the
        // image and the gap is in this workspace's notes.
        // R996: the call now exists, so DataDome joins the wired pair. R995's state was the honest label while the
        // sensor was unwritten; a label is not the work.
        Assert.Equal(VendorWiring.State.Wired, VendorWiring.For("datadome")!.State);
        Assert.Equal(VendorWiring.State.DetectedOnly, VendorWiring.For("imperva")!.State);
        Assert.Equal(VendorWiring.State.DetectedOnly, VendorWiring.For("perimeterx")!.State);
        Assert.Equal(VendorWiring.State.NotAChallenge, VendorWiring.For("queue-it")!.State);

        // the kinds differ in what would unblock them
        Assert.NotEqual(VendorWiring.For("datadome")!.State, VendorWiring.For("queue-it")!.State);
    }

    /// <summary>
    /// R995: the two audits in this repository must not contradict each other.
    ///
    /// <para>
    /// VendorWiring said DataDome had a host and no protocol while WallSolving, in the same source tree, recorded that the
    /// original does solve DataDome and only our notes were short. Both were written down, both had tests, and neither test
    /// could see the other. A disagreement between two tables is invisible to a test that reads one table, so this one reads
    /// both: any vendor WallSolving says the image has a solve method for may not be recorded as
    /// <see cref="VendorWiring.State.HostWithoutProtocol"/> or <see cref="VendorWiring.State.DetectedOnly"/>.
    /// </para>
    /// </summary>
    [Fact]
    public void TheTwoAuditsAgree()
    {
        foreach (var row in VendorWiring.Rows)
        {
            if (!WallSolving.HasSolveFor(row.Vendor)) continue;

            Assert.True(row.State is VendorWiring.State.Wired
                    or VendorWiring.State.OriginalSolvesProtocolUnrecorded,
                $"{row.Vendor} is recorded as {row.State} but WallSolving names a solve method for it, so the original does "
                + "solve it and the missing piece is the call rather than the knowledge. The two audits contradict each other.");
        }
    }

    /// <summary>
    /// R997: two of the six detection markers are not in the image, and the table now says which.
    ///
    /// <para>
    /// kpsdk, queue-it and datadome are image literals -- seventeen, thirteen and fifteen occurrences. cf-chl and
    /// _Incapsula_Resource appear nowhere in it, so the Cloudflare and Imperva detectors were written here rather than
    /// transcribed. Cloudflare works because cf-chl is what a real challenge page carries, but that is general knowledge
    /// and not evidence from the artifact, and a Wired row must not read as though it had been copied.
    /// </para>
    ///
    /// <para>
    /// This test cannot re-probe the binary, so it pins the set that the probe established. Changing it means re-running
    /// <c>python analysis/ida.py str &lt;marker&gt;</c> and finding something there.
    /// </para>
    /// </summary>
    [Fact]
    public void TheMarkerColumnSaysWhereEachMarkerCameFrom()
    {
        var inferred = VendorWiring.Rows
            .Where(r => r.MarkerFrom == VendorWiring.MarkerSource.Inferred)
            .Select(r => r.Vendor)
            .ToList();

        // R1019 moved cloudflare out of this set: cf-chl is in the image zero times, while challenge-platform is
        // there twice as /cdn-cgi/challenge-platform/. That is what "re-run the probe and find something there"
        // looks like, which is the condition this paragraph sets.
        Assert.Equal(new[] { "imperva", "perimeterx" }, inferred);

        foreach (var row in VendorWiring.Rows)
            _out.WriteLine($"{row.Vendor,-12} {row.MarkerFrom,-14} {row.Marker}");
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

        // R944: this used to assert that PerimeterX had no cookie, which was false, and it was the second place that
        // false absence was written down. PerimeterX has _px3.
        Assert.NotNull(AntiBotProtocol.CookiesFor("PerimeterX"));
        Assert.Contains("_px3", AntiBotProtocol.CookiesFor("PerimeterX")!);

        // R945: Imperva's absence is now verified rather than asserted. Searching the image for Imperva and for its four
        // known cookie prefixes -- incap_ses, visid_incap, nlbi_, _Incapsula_ -- returned zero each, so a claim that was
        // written the same way as the false one turns out to be true. Two identical-looking negatives, one false and one
        // true, is the reason a negative has to carry the command that produced it.
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
