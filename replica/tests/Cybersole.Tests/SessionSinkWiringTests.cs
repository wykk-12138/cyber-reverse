using System.Linq;
using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 155: the sink reaches the flush, and the offline case does nothing at all.
///
/// <para>
/// This is the fourth time this session has found the same shape — a working class nobody calls. The
/// interesting part here is the guard: the old flush returned early when <c>SinkUrl</c> was null, so a
/// telemetry-only configuration would have been silently dead. The early return now depends on <b>both</b>
/// destinations being absent.
/// </para>
/// </summary>
public sealed class SessionSinkWiringTests
{
    private readonly ITestOutputHelper _out;

    public SessionSinkWiringTests(ITestOutputHelper output) => _out = output;

    private sealed class CountingSink : ISessionSink
    {
        private readonly bool _configured;

        public CountingSink(bool configured) => _configured = configured;

        public int Calls { get; private set; }

        public bool IsConfigured => _configured;

        public Task<bool> SendAsync(CancellationToken ct = default)
        {
            Calls++;
            return Task.FromResult(true);
        }
    }

    private static SessionPayloadBuilder.Inputs Inputs() => new()
    {
        Sid = "sid", Tid = "tid", Token = "token-token-token-token-token",
        Now = DateTimeOffset.FromUnixTimeMilliseconds(1778830875801),
        TimezoneOffsetMinutes = -120, HasDst = true, DstActive = true,
        StandardOffsetMinutes = -120,
    };

    /// <summary>A configured sink is drained even when there is no request sink.</summary>
    [Fact]
    public async Task ATelemetryOnlyConfigurationStillSends()
    {
        using var analytics = new HttpAnalytics();
        var sink = new CountingSink(configured: true);
        analytics.SessionSink = sink;

        Assert.Null(analytics.SinkUrl);
        analytics.Flush();

        // the send is fire-and-forget, so wait for it rather than assuming
        for (var i = 0; i < 100 && sink.Calls == 0; i++) await Task.Delay(10);

        Assert.Equal(1, sink.Calls);
        _out.WriteLine("a telemetry-only sink is not skipped by the request sink being absent");
    }

    /// <summary>An unconfigured sink is not called, and nothing is queued for it.</summary>
    [Fact]
    public async Task AnUnconfiguredSinkIsNotCalled()
    {
        using var analytics = new HttpAnalytics();
        var sink = new CountingSink(configured: false);
        analytics.SessionSink = sink;

        analytics.Flush();
        await Task.Delay(50);

        Assert.Equal(0, sink.Calls);
    }

    /// <summary>No sink at all: the offline case, which must stay silent.</summary>
    [Fact]
    public async Task TheOfflineCaseDoesNothing()
    {
        using var analytics = new HttpAnalytics();
        analytics.Record(new HttpRequestEvent { Url = "https://example.test/", Status = 200 });

        analytics.Flush();
        await Task.Delay(50);

        // the request stayed buffered, because there is nowhere to send it
        Assert.Single(analytics.Snapshot);
        Assert.Empty(analytics.Failures);
    }

    /// <summary>The Stores-side implementation satisfies the interface through a factory.</summary>
    [Fact]
    public async Task TheImplementationUsesItsFactory()
    {
        ISessionSink sink = new SessionTelemetry("https://analytics.cybersole.io/v1",
            (_, _, _) => Task.FromResult(true));

        Assert.True(sink.IsConfigured);

        // no factory: refused, with a reason, and no transport call
        Assert.False(await sink.SendAsync());

        var telemetry = (SessionTelemetry)sink;
        Assert.Contains("no inputs factory", telemetry.LastError);

        // with a factory: it builds from the current inputs and sends
        string? body = null;
        var wired = new SessionTelemetry("https://analytics.cybersole.io/v1", (_, b, _) =>
        {
            body = b;
            return Task.FromResult(true);
        }) { InputsFactory = Inputs };

        Assert.True(await ((ISessionSink)wired) .SendAsync());
        Assert.Equal(SessionPayloadBuilder.Build(Inputs()).ToString(Newtonsoft.Json.Formatting.None), body);
    }

    /// <summary>A throwing send never reaches the flush caller.</summary>
    [Fact]
    public async Task AThrowingSinkIsRecordedNotThrown()
    {
        using var analytics = new HttpAnalytics();
        analytics.SessionSink = new ThrowingSink();

        analytics.Flush();
        await Task.Delay(100);

        Assert.Contains(analytics.Failures, f => f.Contains("session sink failed", StringComparison.Ordinal));
        _out.WriteLine(analytics.Failures.First());
    }

    private sealed class ThrowingSink : ISessionSink
    {
        public bool IsConfigured => true;

        public Task<bool> SendAsync(CancellationToken ct = default) =>
            throw new InvalidOperationException("boom");
    }
}
