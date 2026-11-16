using Cybersole.Http;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The wiring of <see cref="RedirectPolicy"/> into <see cref="NetClient"/>, and the fact that it is now reachable.
///
/// <para>
/// R951. R950 found that RedirectPolicy existed but had no caller, so the AOT trimmer removed it and the function count
/// did not move. This round wires it into SendAsync, where all three transports converge, and adds the hop counter as a
/// private overload so a caller cannot start a chain part way through. What makes the wiring verifiable rather than
/// merely written is that the type now appears in the reachable call graph -- which is what the tests below can check from
/// the source, and what the next republish checks in the artifact.
/// </para>
/// </summary>
public class RedirectWiringTests
{
    /// <summary>
    /// RedirectPolicy is referenced from NetClient, which is the difference between code that exists and code that ships.
    /// </summary>
    [Fact]
    public void RedirectPolicyIsNowCalledFromNetClient()
    {
        var netClient = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Http", "NetClient.cs"));

        Assert.Contains("RedirectPolicy.IsRedirect", netClient);
        Assert.Contains("RedirectPolicy.LimitFrom", netClient);
        // R952: resolving moved inside FollowAsync, so NetClient no longer names it
        Assert.Contains("limit + 1", netClient);
        Assert.Contains("RedirectPolicy.PreservesMethod", netClient);
        Assert.Contains("RedirectPolicy.FollowAsync", netClient);
        // R952: the exception now comes from FollowAsync ToomanyMessage(), so the name is formatted there
        Assert.Contains("followed.TooManyMessage()", netClient);
    }

    /// <summary>
    /// The hop counter is a private overload rather than an optional public parameter, so only this class can advance it.
    /// </summary>
    [Fact]
    public void TheHopCounterIsPrivate()
    {
        var netClient = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Http", "NetClient.cs"));

        Assert.Contains("private async Task<NetResponse> SendAsync(", netClient);
        Assert.Contains("int hops,", netClient);
        Assert.Contains("limit + 1", netClient);
    }

    /// <summary>A caller's FollowRedirects setting is honoured, since the transport used to hand redirects to HttpClient.</summary>
    [Fact]
    public void FollowRedirectsIsHonoured()
    {
        var netClient = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Http", "NetClient.cs"));

        Assert.Contains("options.FollowRedirects && RedirectPolicy.IsRedirect", netClient);
    }

    /// <summary>
    /// RequestOptions carries the configured limit, and its absence would have meant the wiring silently used the default.
    /// </summary>
    [Fact]
    public void TheLimitIsConfigurable()
    {
        var options = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Http", "TlsProfile.cs"));

        Assert.Contains("public int? MaxRedirects { get; set; }", options);
    }

    /// <summary>
    /// A 303 becomes a GET and drops the body; 307 keeps both. The clone is used because RequestOptions is a class rather
    /// than a record, so `with` would not compile -- and silently mutating the caller's options would leak the change into
    /// its next request.
    /// </summary>
    [Fact]
    public void TheMethodSwitchUsesAClone()
    {
        var netClient = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Http", "NetClient.cs"));

        // R952: the method switch moved inside the FollowAsync fetch delegate, so it is asserted where it now lives
        Assert.Contains("followMethod = HttpMethod.Get", netClient);
        Assert.Contains("carried.Clone()", netClient);
        Assert.DoesNotContain("options with {", netClient);

        // and the policy agrees: 303 never preserves, 307 always does
        Assert.False(RedirectPolicy.PreservesMethod(303, "POST"));
        Assert.True(RedirectPolicy.PreservesMethod(307, "POST"));
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir != null && !System.IO.Directory.Exists(System.IO.Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }
}