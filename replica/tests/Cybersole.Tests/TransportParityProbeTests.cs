using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Why do the two transports return wildly different body sizes for the same URL?
///
/// Observed: SChannel 984,034 bytes vs OwnTls 177,641 bytes against https://www.nike.com/,
/// both HTTP 200. A 5.5x gap on a successful response is worse than an error — online it
/// would look like "the order failed but every log line says 200".
///
/// Working hypotheses, in order of likelihood:
///   1. different Content-Encoding (br vs gzip) and one side decompressed while the other did not
///   2. compressed vs decompressed bytes being counted inconsistently
///   3. OwnTls truncating the body (a real correctness bug)
///
/// This prints the evidence needed to tell them apart.
/// </summary>
[Trait("Speed", "Slow")]
public class TransportParityProbeTests
{
    private readonly ITestOutputHelper _out;
    public TransportParityProbeTests(ITestOutputHelper output) => _out = output;

    private const string Url = "https://www.nike.com/";

    private static void Dump(ITestOutputHelper output, string label, NetResponse r)
    {
        output.WriteLine($"--- {label} ---");
        output.WriteLine($"  status        {r.StatusCode}");
        output.WriteLine($"  protocol      {r.Protocol}");
        output.WriteLine($"  bytes         {r.Bytes}");
        output.WriteLine($"  body.Length   {r.Body.Length}");
        output.WriteLine($"  content-length {Hdr(r, "content-length")}");
        output.WriteLine($"  content-enc    {Hdr(r, "content-encoding")}");
        output.WriteLine($"  transfer-enc   {Hdr(r, "transfer-encoding")}");
        output.WriteLine($"  content-type   {Hdr(r, "content-type")}");
        output.WriteLine($"  first 120      {r.Body.Substring(0, Math.Min(120, r.Body.Length)).Replace('\n', ' ')}");
    }

    private static string Hdr(NetResponse r, string name) =>
        r.Headers.TryGetValue(name, out var v) ? v : "(absent)";

    [Fact]
    public async Task TheTwoTransportsAgreeOnWhatTheServerSent()
    {
        using var system = new NetClient { Transport = TransportMode.SChannel };
        using var own = new NetClient { Transport = TransportMode.OwnTls };

        NetResponse sys;
        try
        {
            sys = await system.GetAsync(Url, new RequestOptions { Tag = "parity-sys" },
                CancellationToken.None);
        }
        catch (Exception ex)
        {
            _out.WriteLine($"system stack unreachable: {ex.Message}");
            return;
        }

        NetResponse mine;
        try
        {
            mine = await own.GetAsync(Url, new RequestOptions { Tag = "parity-own" },
                CancellationToken.None);
        }
        catch (Exception ex)
        {
            _out.WriteLine($"own tls unreachable: {ex.Message}");
            return;
        }

        Dump(_out, "system (SChannel)", sys);
        Dump(_out, "own (Tls12)", mine);

        _out.WriteLine(string.Empty);
        _out.WriteLine($"wire ratio  own/system = {(double)mine.Bytes / Math.Max(1, sys.Bytes):0.00}x" +
                       "   (meaningless across encodings)");
        _out.WriteLine($"body ratio  own/system = {(double)mine.BodyBytes / Math.Max(1, sys.BodyBytes):0.00}x" +
                       "   (the comparable one)");

        var sysEnc = Hdr(sys, "content-encoding");
        var ownEnc = Hdr(mine, "content-encoding");
        _out.WriteLine($"content-encoding: system={sysEnc}  own={ownEnc}");

        // Whatever the server chose to encode with, the decoded bodies must agree. That is the
        // real parity claim, and it is what would catch a truncated body.
        var bodyRatio = (double)mine.BodyBytes / Math.Max(1, sys.BodyBytes);
        Assert.True(bodyRatio > 0.99 && bodyRatio < 1.01,
            $"decoded bodies differ {bodyRatio:0.000}x - one transport is losing content. " +
            $"system={sys.BodyBytes} own={mine.BodyBytes}");
    }
}
