using Cybersole.Http;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The HTTP client's lifecycle, which R910 added because the image names it and this class had an empty Dispose.
///
/// <para>
/// Four of the five highest-leverage absent async names in the whole replica were these: StartAsync referenced
/// nineteen times in the original, HandleResponse eighteen, StopAsync fourteen and DisposeAsyncCore seven. Ranking
/// absent names by occurrence picked them out, which is why R910 worked here rather than on a family that happened to
/// be noticed.
/// </para>
/// </summary>
public class BouncyHttpClientLifecycleTests
{
    /// <summary>A fresh client is usable without an explicit start, because the constructor path has to work before
    /// anything calls StartAsync.</summary>
    [Fact]
    public void ANewClientIsAlreadyRunning()
    {
        using var client = new BouncyHttpClient();
        Assert.True(client.IsRunning);
    }

    [Fact]
    public async Task StartIsIdempotent()
    {
        await using var client = new BouncyHttpClient();
        await client.StartAsync();
        await client.StartAsync();
        Assert.True(client.IsRunning);
    }

    [Fact]
    public async Task StopMakesItNotRunning()
    {
        await using var client = new BouncyHttpClient();
        await client.StopAsync();
        Assert.False(client.IsRunning);
    }

    /// <summary>
    /// A stopped client cannot be restarted. The alternative — letting StartAsync reopen it — would mean a stray call
    /// could resurrect a client whose resources have already been released, and the failure would surface later as a
    /// socket error rather than here.
    /// </summary>
    [Fact]
    public async Task StopIsTerminal()
    {
        await using var client = new BouncyHttpClient();
        await client.StopAsync();

        await Assert.ThrowsAsync<NetException>(() => client.StartAsync());
    }

    /// <summary>Stop is idempotent, so disposing twice does not throw.</summary>
    [Fact]
    public async Task StopIsIdempotent()
    {
        await using var client = new BouncyHttpClient();
        await client.StopAsync();
        await client.StopAsync();
        Assert.False(client.IsRunning);
    }

    /// <summary>
    /// Awaiting disposal stops the client, which is what DisposeAsyncCore is for. Asserted through a client that is
    /// stopped by the await rather than by an explicit call.
    /// </summary>
    [Fact]
    public async Task DisposingAsyncStopsTheClient()
    {
        var client = new BouncyHttpClient();
        Assert.True(client.IsRunning);

        await client.DisposeAsync();

        Assert.False(client.IsRunning);
    }

    /// <summary>
    /// The class is an IAsyncDisposable, which is what makes the DisposeAsyncCore pattern more than a name.
    /// </summary>
    [Fact]
    public void TheClientIsAsyncDisposable()
    {
        Assert.True(typeof(IAsyncDisposable).IsAssignableFrom(typeof(BouncyHttpClient)));
        Assert.True(typeof(IDisposable).IsAssignableFrom(typeof(BouncyHttpClient)));
    }
}
