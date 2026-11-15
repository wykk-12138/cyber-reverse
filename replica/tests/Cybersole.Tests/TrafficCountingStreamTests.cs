using Cybersole.Core.Models;
using Cybersole.Http;
using Xunit;

namespace Cybersole.Tests;

public class TrafficCountingStreamTests
{
    [Fact]
    public async Task Counts_Written_Bytes()
    {
        var proxy = new Proxy();
        using var counting = new TrafficCountingStream(new MemoryStream(), proxy);

        await counting.WriteAsync(new byte[] { 1, 2, 3, 4, 5 });

        Assert.Equal(5, counting.BytesWritten);
    }

    [Fact]
    public async Task Counts_Read_Bytes()
    {
        var proxy = new Proxy();
        var inner = new MemoryStream(new byte[10]);
        using var counting = new TrafficCountingStream(inner, proxy);

        var buffer = new byte[4];
        await counting.ReadAsync(buffer);

        Assert.Equal(4, counting.BytesRead);
    }

    [Fact]
    public void Flushes_Counters_To_The_Proxy_On_Dispose()
    {
        var proxy = new Proxy();
        var counting = new TrafficCountingStream(new MemoryStream(), proxy);
        counting.Write(new byte[7], 0, 7);

        counting.Dispose();

        Assert.Equal(7, proxy.TotalUpload);
        Assert.Equal(0, proxy.TotalDownload);
    }

    [Fact]
    public void Counters_Accumulate_Across_Sessions()
    {
        var proxy = new Proxy { TotalUpload = 100, TotalDownload = 50 };

        using (var first = new TrafficCountingStream(new MemoryStream(), proxy))
            first.Write(new byte[10], 0, 10);

        using (var second = new TrafficCountingStream(new MemoryStream(new byte[3]), proxy))
        {
            var buffer = new byte[3];
            second.Read(buffer, 0, 3);
        }

        Assert.Equal(110, proxy.TotalUpload);
        Assert.Equal(53, proxy.TotalDownload);
    }

    [Fact]
    public void Seeking_Is_Rejected()
    {
        using var counting = new TrafficCountingStream(new MemoryStream(), new Proxy());
        Assert.False(counting.CanSeek);
        Assert.Throws<NotSupportedException>(() => counting.Seek(0, SeekOrigin.Begin));
    }
}
