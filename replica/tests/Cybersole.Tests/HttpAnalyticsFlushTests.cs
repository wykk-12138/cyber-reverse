using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Flush() must never destroy events it cannot deliver.
///
/// Round 127: the body was an empty loop that dequeued first and only then tested SinkUrl, so a
/// build with no sink configured lost its whole buffer the moment anything called Flush(). The
/// timer calls it every ten seconds when autoFlush is on, so the loss was automatic.
/// </summary>
public class HttpAnalyticsFlushTests
{
    private readonly ITestOutputHelper _out;
    public HttpAnalyticsFlushTests(ITestOutputHelper output) => _out = output;

    private static HttpRequestEvent Evt(int i) => new()
    {
        Url = $"https://example.com/{i}",
        Method = "GET",
        Status = 200,
        ElapsedMs = 10 + i,
        Bytes = 512,
        Protocol = "h2",
        Tag = "test",
    };

    [Fact]
    public void Flush_WithNoSink_KeepsEveryEvent()
    {
        using var analytics = new HttpAnalytics();
        for (var i = 0; i < 5; i++) analytics.Record(Evt(i));

        Assert.Equal(5, analytics.Snapshot.Count);

        analytics.Flush();          // no SinkUrl
        analytics.Flush();          // and again, because the timer would

        Assert.Equal(5, analytics.Snapshot.Count);
        _out.WriteLine($"kept {analytics.Snapshot.Count} of 5 after two flushes with no sink");
    }

    [Fact]
    public void Flush_WithSink_DrainsOnlyWhatItCanSend()
    {
        // BatchSize is set above the number recorded so Record() does not auto-flush; the point
        // here is Flush()'s own behaviour.
        using var analytics = new HttpAnalytics { SinkUrl = "http://127.0.0.1:9/", BatchSize = 100 };
        for (var i = 0; i < 7; i++) analytics.Record(Evt(i));

        Assert.Equal(7, analytics.Snapshot.Count);

        analytics.Flush();

        Assert.Equal(0, analytics.Snapshot.Count);
        _out.WriteLine("all 7 drained in one batch when BatchSize allows it");
    }

    [Fact]
    public void BatchSize_CapsOneFlush()
    {
        using var analytics = new HttpAnalytics { SinkUrl = "http://127.0.0.1:9/", BatchSize = 100 };
        for (var i = 0; i < 7; i++) analytics.Record(Evt(i));

        // lower the cap after recording so Record()'s own auto-flush stays out of the way
        analytics.BatchSize = 3;
        analytics.Flush();

        Assert.Equal(4, analytics.Snapshot.Count);
        _out.WriteLine($"BatchSize=3 left {analytics.Snapshot.Count} of 7");
    }

    [Fact]
    public void Flush_WithSink_DoesNotBlockTheCaller()
    {
        using var analytics = new HttpAnalytics { SinkUrl = "http://10.255.255.1:9/", BatchSize = 100 };
        analytics.Record(Evt(0));

        // 10.255.255.1 is non-routable: a synchronous post would hang far longer than this
        var started = DateTime.UtcNow;
        analytics.Flush();
        var elapsed = (DateTime.UtcNow - started).TotalMilliseconds;

        Assert.True(elapsed < 500, $"Flush took {elapsed:0} ms — analytics must not stall a request");
        _out.WriteLine($"Flush returned in {elapsed:0} ms against a non-routable sink");
    }
}
