using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Queue-it, read out of a class's field list: host markers, the accepted-cookie prefix with its hash, validity seconds,
/// and a minimum remaining.
///
/// <para>
/// R959. The image carries a concatenated field list — QueueHostMarkers, AcceptedCookiePrefix, CookieValiditySeconds,
/// MinRemainingSeconds — and the prefix is QueueITAccepted-SDFrts345E-V3_ with a literal hash in it. It also carries five
/// control-flow messages, one of which is misspelled, and the misspelling is kept because a replica that fixes it stops
/// matching the original's own log.
/// </para>
/// </summary>
public class QueueItProtocolTests
{
    /// <summary>Hosts are recognised by suffix or by the waiting-room prefix, and nothing else is.</summary>
    [Theory]
    [InlineData("shop.queue-it.net", true)]
    [InlineData("panini.queue-it.net", true)]
    [InlineData("waitingroom.example.com", true)]
    [InlineData("example.com", false)]
    [InlineData("queue-it.net.evil.com", false)]
    [InlineData(null, false)]
    public void HostRecognition(string? host, bool expected)
    {
        Assert.Equal(expected, QueueItProtocol.IsQueueHost(host));
    }

    /// <summary>The pass cookie's prefix carries a hash that is part of the name, so it is kept verbatim.</summary>
    [Fact]
    public void TheCookiePrefixIsVerbatim()
    {
        Assert.Equal("QueueITAccepted-SDFrts345E-V3_", QueueItProtocol.AcceptedCookiePrefix);

        Assert.Equal("QueueITAccepted-SDFrts345E-V3_abc", QueueItProtocol.CookieName("abc"));
        Assert.True(QueueItProtocol.IsAcceptedCookie("QueueITAccepted-SDFrts345E-V3_abc"));
        Assert.False(QueueItProtocol.IsAcceptedCookie("QueueITAccepted-OTHER_abc"));
        Assert.False(QueueItProtocol.IsAcceptedCookie(null));
    }

    /// <summary>
    /// A pass about to expire is worse than none, because the request it authorises fails after the queue has been left.
    /// So usability is a remaining-time question, not a validity question.
    /// </summary>
    [Fact]
    public void UsabilityIsAboutRemainingTime()
    {
        var now = new DateTimeOffset(2026, 11, 17, 10, 0, 0, TimeSpan.Zero);
        var min = TimeSpan.FromSeconds(30);

        Assert.True(QueueItProtocol.IsUsable(now.AddMinutes(5), now, min));
        Assert.True(QueueItProtocol.IsUsable(now.AddSeconds(31), now, min));
        Assert.False(QueueItProtocol.IsUsable(now.AddSeconds(29), now, min));

        // valid but expiring inside the margin: still unusable
        Assert.False(QueueItProtocol.IsUsable(now.AddSeconds(5), now, min));
    }

    /// <summary>Status and pass together decide the verdict, because one status can mean two things.</summary>
    [Theory]
    [InlineData(401, false, QueueVerdict.Banned)]
    [InlineData(403, false, QueueVerdict.Banned)]
    [InlineData(429, false, QueueVerdict.RetryLater)]
    [InlineData(200, true, QueueVerdict.Passed)]
    [InlineData(200, false, QueueVerdict.Waiting)]
    [InlineData(404, false, QueueVerdict.Failed)]
    public void VerdictFromStatusAndPass(int status, bool hasPass, QueueVerdict expected)
    {
        Assert.Equal(expected, QueueItProtocol.Verdict(status, hasPass));
    }

    /// <summary>A 200 with a pass is passed even though the status alone would read as waiting.</summary>
    [Fact]
    public void ThePassOutranksTheStatus()
    {
        Assert.Equal(QueueVerdict.Waiting, QueueItProtocol.Verdict(200, false));
        Assert.Equal(QueueVerdict.Passed, QueueItProtocol.Verdict(200, true));
    }

    /// <summary>The messages are the image's, including the misspelling.</summary>
    [Fact]
    public void TheMessagesKeepTheMisspelling()
    {
        var messages = (string[])typeof(QueueItProtocol)
            .GetField("Messages", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static)!
            .GetValue(null)!;

        Assert.Contains("Fetching Queue-it challenge", messages);
        Assert.Contains("Initiliazing Queue-it", messages);          // the image's spelling
        Assert.Contains("Error Initiliazing Queue-it (Softblock)", messages);
        Assert.Contains("Queue-IT banned, rotating proxy", messages);

        Assert.DoesNotContain("Initializing Queue-it", messages);
    }

    /// <summary>Three handler spellings exist in the image, so all three are recorded.</summary>
    [Fact]
    public void TheThreeHandlerSpellingsAreRecorded()
    {
        var handlers = (string[])typeof(QueueItProtocol)
            .GetField("HandlerNames", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static)!
            .GetValue(null)!;

        Assert.Equal(new[] { "QueueItHandler", "queueItHandler", "_queueItHandler" }, handlers);
    }

    /// <summary>Each verdict has a description, and the waiting one is the image's challenge message.</summary>
    [Fact]
    public void EveryVerdictDescribesItself()
    {
        foreach (var verdict in Enum.GetValues<QueueVerdict>())
            Assert.False(string.IsNullOrWhiteSpace(QueueItProtocol.Describe(verdict)));

        Assert.Equal("Fetching Queue-it challenge", QueueItProtocol.Describe(QueueVerdict.Waiting));
        Assert.Equal("Queue-IT banned, rotating proxy", QueueItProtocol.Describe(QueueVerdict.Banned));
    }
}