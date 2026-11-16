using System.Linq;
using Cybersole.Http;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Redirect following and throttling, the first branch-heavy code this session rather than another constant table.
///
/// <para>
/// R950. The image names MaxRedirects, TooManyRedirects, Retry-After with its [Throttling] log prefix, and
/// cbsPollingRetryAttempts. The replica had none of them, so this is logic where the last dozen rounds added tables -- and
/// R949 measured that difference: tables add no functions, logic added 1,963.
/// </para>
/// </summary>
public class RedirectPolicyTests
{
    /// <summary>Statuses that redirect, and one that does not despite sitting in the same range.</summary>
    [Theory]
    [InlineData(301, true)]
    [InlineData(302, true)]
    [InlineData(303, true)]
    [InlineData(307, true)]
    [InlineData(308, true)]
    [InlineData(304, false)]   // a cache validator, not a hop
    [InlineData(200, false)]
    [InlineData(404, false)]
    public void RedirectStatuses(int status, bool expected)
    {
        Assert.Equal(expected, RedirectPolicy.IsRedirect(status));
    }

    /// <summary>307 and 308 keep the method unconditionally; 303 never does; 301/302 keep it only for GET and HEAD.</summary>
    [Theory]
    [InlineData(307, "POST", true)]
    [InlineData(308, "POST", true)]
    [InlineData(303, "POST", false)]
    [InlineData(302, "POST", false)]
    [InlineData(302, "GET", true)]
    [InlineData(301, "HEAD", true)]
    public void MethodPreservation(int status, string method, bool expected)
    {
        Assert.Equal(expected, RedirectPolicy.PreservesMethod(status, method));
    }

    /// <summary>A non-positive configured limit means "do not follow", not "unlimited".</summary>
    [Theory]
    [InlineData(null, 10)]
    [InlineData(0, 10)]
    [InlineData(-5, 10)]
    [InlineData(3, 3)]
    public void TheLimitFallsBackRatherThanOpening(int? configured, int expected)
    {
        Assert.Equal(expected, RedirectPolicy.LimitFrom(configured));
    }

    /// <summary>A chain that ends normally stops on the first non-redirect.</summary>
    [Fact]
    public async Task AChainTerminates()
    {
        var hops = new Dictionary<string, RedirectHop>
        {
            ["https://a/1"] = new(302, "https://a/2"),
            ["https://a/2"] = new(301, "/3"),
            ["https://a/3"] = new(200, null),
        };

        var result = await RedirectPolicy.FollowAsync("https://a/1", (u, _) => Task.FromResult(hops[u]));

        Assert.False(result.TooMany);
        Assert.Equal(200, result.StatusCode);
        Assert.Equal(2, result.Hops);
        Assert.Equal("https://a/3", result.FinalUrl);
    }

    /// <summary>
    /// A self-redirect consumes hops like any other, so a cycle terminates at the limit rather than spinning.
    /// </summary>
    [Fact]
    public async Task ASelfRedirectConsumesHops()
    {
        var result = await RedirectPolicy.FollowAsync(
            "https://a/loop",
            (_, _) => Task.FromResult(new RedirectHop(302, "https://a/loop")),
            maxRedirects: 3);

        Assert.True(result.TooMany);
        Assert.Equal(3, result.Hops);
        Assert.Contains("TooManyRedirects", result.TooManyMessage());
    }

    /// <summary>The exception message names the chain, so a runaway is diagnosable from the log alone.</summary>
    [Fact]
    public async Task TheTooManyMessageCarriesTheChain()
    {
        var result = await RedirectPolicy.FollowAsync(
            "https://a/x",
            (_, _) => Task.FromResult(new RedirectHop(307, "https://a/x")),
            maxRedirects: 2);

        var message = result.TooManyMessage();
        Assert.StartsWith("TooManyRedirects", message);
        Assert.Contains("2 hops", message);
        Assert.Contains("https://a/x", message);
    }

    /// <summary>A relative Location resolves against its own request, not against the start of the chain.</summary>
    [Fact]
    public void RelativeLocationsResolveAgainstTheCurrentUrl()
    {
        Assert.Equal("https://a/b/c", RedirectPolicy.Resolve("https://a/b/start", "c"));
        Assert.Equal("https://a/x", RedirectPolicy.Resolve("https://a/b/start", "/x"));
        Assert.Equal("https://other/y", RedirectPolicy.Resolve("https://a/b/start", "https://other/y"));
    }

    /// <summary>
    /// Both Retry-After forms: seconds, and an HTTP date. A date read as a number would give zero and retry into the same
    /// throttle, which is why both are parsed.
    /// </summary>
    [Fact]
    public void RetryAfterHandlesBothForms()
    {
        var fallback = TimeSpan.FromSeconds(30);

        Assert.Equal(TimeSpan.FromSeconds(5), RedirectPolicy.ParseRetryAfter("5", fallback));

        var soon = DateTimeOffset.UtcNow.AddSeconds(60).ToString("R");
        var parsed = RedirectPolicy.ParseRetryAfter(soon, fallback);
        Assert.InRange(parsed.TotalSeconds, 50, 60);
    }

    /// <summary>An unparseable value falls back rather than returning zero, because zero is the one certain mistake.</summary>
    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData("soon")]
    [InlineData("1.2.3")]
    public void UnparseableFallsBack(string? value)
    {
        var fallback = TimeSpan.FromSeconds(7);
        Assert.Equal(fallback, RedirectPolicy.ParseRetryAfter(value, fallback));
    }

    /// <summary>Throttling is a status plus a header, and the log line uses the image's own wording.</summary>
    [Fact]
    public void ThrottlingIsLoggedInTheImagesWording()
    {
        Assert.True(RedirectPolicy.IsThrottled(429, "5"));
        Assert.True(RedirectPolicy.IsThrottled(503, "5"));
        Assert.False(RedirectPolicy.IsThrottled(429, null));
        Assert.False(RedirectPolicy.IsThrottled(200, "5"));

        var line = RedirectPolicy.ThrottleLog(429, TimeSpan.FromSeconds(12));
        Assert.StartsWith("[Throttling] Retry-After header detected, ", line);
        Assert.Contains("429", line);
        Assert.Contains("12", line);
    }
}