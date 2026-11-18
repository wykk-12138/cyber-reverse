using System.Text.Json;
using Cybersole.Http;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// WHY THIS EXISTS: obtaining a token and having it accepted are different facts, and the Kasada endpoints
/// themselves will not tell them apart — measured on the live site, /fp issues a token to any request shape
/// and /tl answers 200 to an empty body carrying a forged token. So the only honest test of acceptance is
/// to call the endpoint twice, once bare and once with the credentials, and compare. These cases pin that
/// comparison rather than the outcome of any particular site.
/// </summary>
public sealed class KasadaGateProbeTests
{
    private static KasadaHttpHandshake Handshake(
        Func<string, string, Dictionary<string, string>, (int, string)> respond, out NetClient http)
    {
        http = new NetClient();
        return new KasadaHttpHandshake(http)
        {
            Transport = (url, method, headersJson, body) =>
            {
                var sent = JsonSerializer.Deserialize<Dictionary<string, string>>(headersJson) ?? new();
                var (status, payload) = respond(url, method, sent);
                var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
                if (url.EndsWith("/fp", StringComparison.Ordinal) || url.Contains("/fp?", StringComparison.Ordinal))
                    headers["x-kpsdk-ct"] = "TOKEN-FROM-FP";
                return JsonSerializer.Serialize(new { status, headers, body = payload });
            },
        };
    }

    private const string ScriptUrl =
        "https://api.nike.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/p.js";

    [Fact]
    public async Task AGatedEndpointShowsUpAsGated()
    {
        // The endpoint refuses a bare call and answers a credentialed one: that difference is the evidence.
        var handshake = Handshake((url, method, headers) =>
        {
            // The handshake's own hops always succeed; only the probed endpoint is gated.
            if (url.Contains("/mfc", StringComparison.Ordinal) || url.Contains("/fp", StringComparison.Ordinal)
                || url.Contains("/ips.js", StringComparison.Ordinal)) return (200, "");
            return headers.ContainsKey("x-kpsdk-ct") ? (200, "PROTECTED DATA") : (403, "");
        }, out var http);
        using (http)
        {
            var ran = await handshake.RunAsync(ScriptUrl);
            Assert.True(ran, "handshake failed: " + handshake.Error);
            Assert.False(string.IsNullOrEmpty(handshake.ClientToken), "no token to offer");
            Assert.True(handshake.RequestHeaders().ContainsKey("x-kpsdk-ct"), "token missing from headers");

            var probe = await handshake.ProbeAsync("https://example.test/protected");

            Assert.True(probe.Gated, probe.ToString());
            Assert.Equal(403, probe.BareStatus);
            Assert.Equal(200, probe.TokenStatus);
        }
    }

    [Fact]
    public async Task AnEndpointThatDoesNotCareShowsUpAsUngated()
    {
        // Measured against Nike's own product feed: the same answer either way, which means the token is
        // not what that endpoint wants -- not that the token is invalid.
        var handshake = Handshake((url, method, headers) => (200, "SAME"), out var http);
        using (http)
        {
            await handshake.RunAsync(ScriptUrl);
            var probe = await handshake.ProbeAsync("https://example.test/open");

            Assert.False(probe.Gated);
            Assert.Equal(probe.BareStatus, probe.TokenStatus);
            Assert.Equal(probe.BareLength, probe.TokenLength);
        }
    }

    [Fact]
    public async Task AnUnreachableEndpointIsReportedRatherThanThrown()
    {
        var http = new NetClient();
        using (http)
        {
            var handshake = new KasadaHttpHandshake(http);
            var probe = await handshake.ProbeAsync("http://127.0.0.1:1/protected");

            Assert.False(probe.Gated);
            Assert.Equal(0, probe.BareStatus);
            Assert.False(string.IsNullOrEmpty(probe.BareError));
        }
    }

    [Fact]
    public async Task TheCredentialsTravelOnTheProbedCall()
    {
        List<Dictionary<string, string>> seen = new();
        var handshake = Handshake((url, method, headers) =>
        {
            seen.Add(headers);
            return (200, "ok");
        }, out var http);
        using (http)
        {
            await handshake.RunAsync(ScriptUrl);
            seen.Clear();
            await handshake.ProbeAsync("https://example.test/protected");

            Assert.Equal(2, seen.Count);
            // First call bare, second carrying the token: the order is what makes the comparison meaningful.
            Assert.False(seen[0].ContainsKey("x-kpsdk-ct"));
            Assert.True(seen[1].ContainsKey("x-kpsdk-ct"));
        }
    }
}
