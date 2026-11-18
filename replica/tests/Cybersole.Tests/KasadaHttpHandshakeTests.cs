using System.Text.Json;
using Cybersole.Http;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// WHY THIS EXISTS: the no-browser handshake is the road that has to be reusable outside this application,
/// so its order and its header plumbing are pinned rather than described. Measured on the live site
/// (docs/KASADA/11 section 6): mfc gives the config, fp gives the first token, ips.js with that token as
/// KP_UIDz gives the token a protected request actually carries.
/// </summary>
public sealed class KasadaHttpHandshakeTests
{
    /// <summary>A fake server that answers the three hops and records what it was asked.</summary>
    private sealed class FakeServer
    {
        public List<string> Calls { get; } = new();

        public string Answer(string url, string method, string headersJson, string body)
        {
            Calls.Add(url);

            var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            if (url.EndsWith("/mfc", StringComparison.Ordinal))
            {
                headers["x-kpsdk-h"] = "01FINGERPRINT=";
                headers["x-kpsdk-fc"] = "eyJmZWF0dXJlRmxhZ3MiOnt9fQ==";
            }
            else if (url.Contains("/fp?", StringComparison.Ordinal))
            {
                headers["x-kpsdk-ct"] = "FIRST-TOKEN-0123456789";
                headers["x-kpsdk-r"] = "1-AA";
            }
            else if (url.Contains("/ips.js?", StringComparison.Ordinal))
            {
                headers["x-kpsdk-ct"] = "FINAL-TOKEN-0123456789";
                headers["x-kpsdk-r"] = "1-AA";
            }

            headers["Content-Type"] = "application/json";
            return JsonSerializer.Serialize(new { status = 200, headers, body = "" });
        }
    }

    private static KasadaHttpHandshake Handshake(FakeServer server, out NetClient http)
    {
        http = new NetClient();
        var handshake = new KasadaHttpHandshake(http)
        {
            Transport = server.Answer,
        };
        return handshake;
    }

    private const string ScriptUrl =
        "https://api.nike.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/p.js";

    [Fact]
    public async Task TheThreeHopsRunInOrderAndEndWithTheSecondToken()
    {
        var server = new FakeServer();
        var handshake = Handshake(server, out var http);
        using (http)
        {
            var ok = await handshake.RunAsync(ScriptUrl);

            Assert.True(ok, handshake.Error);
            Assert.Equal(3, server.Calls.Count);

            // The UUID directory is part of the address; the bare origin 404s there.
            Assert.All(server.Calls, u => Assert.StartsWith(handshake.Root!, u, StringComparison.Ordinal));
            Assert.Contains("/mfc", server.Calls[0]);
            Assert.Contains("/fp?", server.Calls[1]);

            // The second token is the one a protected request carries, and it is fetched with the first.
            Assert.Contains("KP_UIDz=FIRST-TOKEN-0123456789", server.Calls[2]);
            Assert.Equal("FINAL-TOKEN-0123456789", handshake.ClientToken);
        }
    }

    [Fact]
    public async Task TheBuildTravelsOnTheTokenRequest()
    {
        var server = new FakeServer();
        var handshake = Handshake(server, out var http);
        using (http)
        {
            handshake.Build = "j-9.9.999";
            await handshake.RunAsync(ScriptUrl);
            Assert.Contains("/fp?x-kpsdk-v=j-9.9.999", server.Calls[1]);
        }
    }

    [Fact]
    public async Task EveryHeaderTheHandshakeSawIsAvailableToTheProtectedRequest()
    {
        var server = new FakeServer();
        var handshake = Handshake(server, out var http);
        using (http)
        {
            await handshake.RunAsync(ScriptUrl);

            var headers = handshake.RequestHeaders();
            Assert.Equal("FINAL-TOKEN-0123456789", headers["x-kpsdk-ct"]);
            Assert.Equal("01FINGERPRINT=", headers["x-kpsdk-h"]);
            Assert.Equal("eyJmZWF0dXJlRmxhZ3MiOnt9fQ==", headers["x-kpsdk-fc"]);
            Assert.Equal("1-AA", headers["x-kpsdk-r"]);
            Assert.Equal(KasadaVersions.Observed, headers["x-kpsdk-v"]);
        }
    }

    [Fact]
    public async Task ARelativeScriptUrlIsRefusedWithoutAnyRequest()
    {
        var server = new FakeServer();
        var handshake = Handshake(server, out var http);
        using (http)
        {
            Assert.False(await handshake.RunAsync("/p.js"));
            Assert.Empty(server.Calls);
            Assert.False(string.IsNullOrEmpty(handshake.Error));
        }
    }

    [Fact]
    public async Task AFailingFirstHopStopsCleanlyWithNoToken()
    {
        var server = new FakeServer();
        var http = new NetClient();
        using (http)
        {
            var handshake = new KasadaHttpHandshake(http)
            {
                // A step that reports failure must not leave a half-built token behind.
                Transport = (url, method, headers, body) => url.EndsWith("/mfc", StringComparison.Ordinal)
                    ? JsonSerializer.Serialize(new { status = 403, headers = new Dictionary<string, string>(), body = "" })
                    : server.Answer(url, method, headers, body),
            };

            Assert.False(await handshake.RunAsync(ScriptUrl));
            Assert.Null(handshake.ClientToken);
        }
    }
}
