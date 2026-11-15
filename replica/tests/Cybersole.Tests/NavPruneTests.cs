using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 163: the prune list, which corrects R156, and the credentials shim, which stays an open item.
///
/// <para>
/// The image's mobile script deletes nine Blink-only members rather than trapping them —
/// <c>userAgentData</c>, <c>getBattery</c>, <c>connection</c>, <c>bluetooth</c>, <c>usb</c>, <c>hid</c>, <c>serial</c>,
/// <c>xr</c>, <c>deviceMemory</c> — because "browserleaks reads every one of them straight off navigator". R156
/// installed <c>connection</c> for every profile, which is right for the desktop sample and wrong for a phone.
/// </para>
/// </summary>
public sealed class NavPruneTests
{
    private readonly ITestOutputHelper _out;

    public NavPruneTests(ITestOutputHelper output) => _out = output;

    /// <summary>Nine members, exactly the ones the comment names.</summary>
    [Fact]
    public void ThePruneListIsTheCommentsList()
    {
        Assert.Equal(9, NavPrune.BlinkOnly.Count);
        Assert.Equal(new[]
        {
            "userAgentData", "getBattery", "connection", "bluetooth", "usb", "hid", "serial", "xr",
            "deviceMemory",
        }, NavPrune.BlinkOnly);

        _out.WriteLine(string.Join(", ", NavPrune.BlinkOnly));
    }

    /// <summary>Deleting is the mechanism, and it happens on both the instance and the prototype.</summary>
    [Fact]
    public void TheBodyDeletes()
    {
        var js = NavPrune.BodyJs();

        // R169: whitelist, not blacklist — delete every own name on the prototype that is not kept
        Assert.Contains("const sweep = (target)", js);
        Assert.Contains("own(target).forEach((key) => {", js);
        Assert.Contains("delete target[key]", js);
        Assert.Contains("key !== 'constructor'", js);

        // the allowlist is what the body carries; `connection` is deliberately not on it
        Assert.Contains("'plugins'", js);
        Assert.Contains("'mimeTypes'", js);
        Assert.DoesNotContain("'connection'", js);
        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
    }

    /// <summary>Only an Apple profile prunes; the desktop sample reads connection and must keep it.</summary>
    [Fact]
    public void OnlyAnAppleProfilePrunes()
    {
        Assert.True(NavPrune.ShouldPrune(
            "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) AppleWebKit/605.1.15"));
        Assert.False(NavPrune.ShouldPrune(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " +
            "Chrome/157.0.0.0 Safari/537.36"));

        // and the desktop payload does read it — R152's sample carries the connection quartet
        Assert.Contains("navigator.connection.effectiveType", SessionPayload.ConnectionKeys);
    }

    /// <summary>The credentials shim's four triples, and the open item stated as one.</summary>
    [Fact]
    public void TheCredentialsShimIsRecordedNotBuilt()
    {
        Assert.Equal(4, NavPrune.Credentials.Count);
        Assert.Equal(new[] { "get", "create", "preventSilentAccess", "store" },
            NavPrune.Credentials.Select(c => c.Name));

        Assert.Equal(1, NavPrune.Credentials[0].Length);
        Assert.Equal(1, NavPrune.Credentials[1].Length);
        Assert.Equal(0, NavPrune.Credentials[2].Length);
        Assert.Equal(1, NavPrune.Credentials[3].Length);

        Assert.All(NavPrune.Credentials, c => Assert.False(c.Implemented));

        Assert.Contains("virtual authenticator", NavPrune.CredentialsOpenItem);
        Assert.Contains("has not built", NavPrune.CredentialsOpenItem);

        _out.WriteLine(NavPrune.CredentialsOpenItem);
    }

    /// <summary>The rule states the two-claim fact.</summary>
    [Fact]
    public void TheRuleStands()
    {
        Assert.Contains("installed for one claim and deleted for another", NavPrune.Rule);
    }
}
