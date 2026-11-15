using Cybersole.Http;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The TLS session pool's bookkeeping. The network half needs a live host, so these cover the
/// decisions that make pooling safe: what gets reused, what gets thrown away, and what happens
/// after disposal.
/// </summary>
public class Tls12PoolTests
{
    [Fact]
    public void AFreshPoolHoldsNothing()
    {
        using var pool = new Tls12Pool();
        Assert.Equal(0, pool.IdleCount);
    }

    [Fact]
    public void DiscardAcceptsNullAndDoesNotThrow()
    {
        using var pool = new Tls12Pool();
        pool.Discard(null);
        Assert.Equal(0, pool.IdleCount);
    }

    [Fact]
    public void DisposingTwiceIsSafe()
    {
        var pool = new Tls12Pool();
        pool.Dispose();
        pool.Dispose();
        Assert.Equal(0, pool.IdleCount);
    }

    [Fact]
    public void ReturnAfterDisposeClosesInsteadOfStoring()
    {
        var pool = new Tls12Pool();
        pool.Dispose();

        // a null client keeps this network-free while still exercising the guard
        pool.Return("example.com", 443, TlsProfile.Chrome, null!);
        Assert.Equal(0, pool.IdleCount);
    }

    [Fact]
    public void MaxIdleIsWellUnderTheUsualServerTimeout()
    {
        // Servers commonly drop idle TLS sockets at 60-120s. Sitting under that is what keeps
        // a rented connection from failing mid-request, so pin the number.
        Assert.True(Tls12Pool.MaxIdle < TimeSpan.FromSeconds(60),
            $"MaxIdle is {Tls12Pool.MaxIdle}, which risks racing a server-side idle close");
        Assert.True(Tls12Pool.MaxIdle >= TimeSpan.FromSeconds(10),
            "MaxIdle is so short that pooling would rarely help");
    }
}
