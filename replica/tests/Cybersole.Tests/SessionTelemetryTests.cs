using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 154: the payload has a sender, and the sender refuses to send anywhere the image did not name.
///
/// <para>
/// This is the round where a mistake would have been invisible: a telemetry sender pointed at an unset or
/// misspelled host posts a fingerprint somewhere and reports success. Both guards are pinned here without a
/// network, because the transport is injected.
/// </para>
/// </summary>
public sealed class SessionTelemetryTests
{
    private readonly ITestOutputHelper _out;

    public SessionTelemetryTests(ITestOutputHelper output) => _out = output;

    private static SessionPayloadBuilder.Inputs Inputs() => new()
    {
        Sid = "sid-1",
        Tid = "tid-1",
        Token = "ASaMBHzL7WoRfLL6ekqt4MuLNpqk5pjk",
        Now = DateTimeOffset.FromUnixTimeMilliseconds(1778830875801),
        TimezoneOffsetMinutes = -120,
        HasDst = true,
        DstActive = true,
        StandardOffsetMinutes = -120,
        TimeString = "Fri May 15 2026 09:41:15 GMT+0200 (Midden-Europese zomertijd)",
    };

    /// <summary>No sink means no send, and the reason says so.</summary>
    [Fact]
    public async Task WithoutASinkNothingIsSent()
    {
        var calls = 0;
        var telemetry = new SessionTelemetry(post: (_, _, _) =>
        {
            calls++;
            return Task.FromResult(true);
        });

        Assert.False(telemetry.IsConfigured);

        var sent = await telemetry.SendAsync(Inputs());

        Assert.False(sent);
        Assert.Equal(0, calls);
        Assert.Contains("no sink configured", telemetry.LastError);
    }

    /// <summary>A host the image does not name is refused by name.</summary>
    [Fact]
    public async Task AnUnknownHostIsRefused()
    {
        foreach (var host in new[]
                 {
                     "https://example.test/collect", "https://api.cybersole.io/session",
                     "https://analytics.cybersole.io.evil.test/x", "not a url",
                 })
        {
            var calls = 0;
            var telemetry = new SessionTelemetry(host, (_, _, _) =>
            {
                calls++;
                return Task.FromResult(true);
            });

            var sent = await telemetry.SendAsync(Inputs());

            Assert.False(sent);
            Assert.Equal(0, calls);
            Assert.Contains("not one of the recorded hosts", telemetry.LastError);
        }

        _out.WriteLine(string.Join(", ", SessionTelemetry.AllowedHosts));
    }

    /// <summary>Both allowed hosts send exactly the payload the builder makes.</summary>
    [Fact]
    public async Task BothAllowedHostsSendTheBuiltPayload()
    {
        foreach (var host in SessionTelemetry.AllowedHosts)
        {
            string? received = null;
            var telemetry = new SessionTelemetry("https://" + host + "/v1/session", (url, body, _) =>
            {
                Assert.Contains(host, url, StringComparison.Ordinal);
                received = body;
                return Task.FromResult(true);
            });

            Assert.True(telemetry.IsConfigured);

            var sent = await telemetry.SendAsync(Inputs());

            Assert.True(sent, host);
            Assert.Null(telemetry.LastError);
            Assert.NotNull(received);
            Assert.Equal(SessionPayloadBuilder.Build(Inputs()).ToString(Newtonsoft.Json.Formatting.None),
                received);
        }
    }

    /// <summary>A transport that refuses is reported, not thrown.</summary>
    [Fact]
    public async Task ARefusingTransportIsReported()
    {
        var telemetry = new SessionTelemetry("https://telemetry.cybersole.io/v1",
            (_, _, _) => Task.FromResult(false));

        var sent = await telemetry.SendAsync(Inputs());

        Assert.False(sent);
        Assert.Equal("transport refused the payload", telemetry.LastError);
    }

    /// <summary>A throwing transport is reported too — telemetry is never on the critical path.</summary>
    [Fact]
    public async Task AThrowingTransportIsReported()
    {
        var telemetry = new SessionTelemetry("https://analytics.cybersole.io/v1",
            (_, _, _) => throw new InvalidOperationException("socket closed"));

        var sent = await telemetry.SendAsync(Inputs());

        Assert.False(sent);
        Assert.Contains("socket closed", telemetry.LastError);
    }

    /// <summary>A cancelled send stops and says so.</summary>
    [Fact]
    public async Task CancellationIsReported()
    {
        var telemetry = new SessionTelemetry("https://analytics.cybersole.io/v1",
            (_, _, ct) => throw new OperationCanceledException(ct));

        var sent = await telemetry.SendAsync(Inputs());

        Assert.False(sent);
        Assert.Equal("cancelled", telemetry.LastError);
    }

    /// <summary>The allowed hosts are a subset of the fifteen the image names.</summary>
    [Fact]
    public void TheAllowedHostsComeFromTheRecordedFifteen()
    {
        Assert.Equal(2, SessionTelemetry.AllowedHosts.Length);

        foreach (var host in SessionTelemetry.AllowedHosts)
            Assert.True(CybersoleHosts.IsKnown(host), host);

        // and neither is a solver host — this payload is not a challenge answer
        foreach (var host in SessionTelemetry.AllowedHosts)
            Assert.False(CybersoleHosts.IsSolverHost(host), host);

        _out.WriteLine("both sinks are ordinary Cybersole hosts, neither solves a wall");
    }
}
