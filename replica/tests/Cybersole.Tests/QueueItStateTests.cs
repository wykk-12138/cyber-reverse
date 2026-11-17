using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1025: Queue-it was the audit's only NotAChallenge row, on the reasoning that a queue is a queue and the handling is
/// to wait. The image says a waiting room is one of two things this vendor does.
///
/// <para>
/// Eight literals carry the other one: a fetch of the vendor's challenge, solving and initialising failures on its
/// softblock, a BotDeflector page the original explicitly calls unsupported, the /softblock endpoint, a
/// queueitcaptcha challenge endpoint, and seven X-queueit-challange-* headers running as deep as ruleid and rulename.
/// So the row's original claim was half right -- waiting is part of the handling -- and its conclusion that waiting was
/// all of it was the mistake.
/// </para>
/// </summary>
public sealed class QueueItStateTests
{
    /// <summary>The row no longer claims a queue is not a challenge.</summary>
    [Fact]
    public void TheRowIsNoLongerNotAChallenge()
    {
        var row = VendorWiring.Rows.Single(r => r.Vendor == "queue-it");

        Assert.NotEqual(VendorWiring.State.NotAChallenge, row.State);
        Assert.Equal(VendorWiring.State.DetectedOnly, row.State);
    }

    /// <summary>Its marker was never in doubt, so the gap column is untouched by this correction.</summary>
    [Fact]
    public void TheMarkerAndGapAreUnchanged()
    {
        var row = VendorWiring.Rows.Single(r => r.Vendor == "queue-it");

        Assert.Equal("queue-it", row.Marker);
        Assert.Equal(VendorWiring.MarkerSource.ImageLiteral, row.MarkerFrom);
        Assert.Equal(VendorWiring.Gap.None, row.Gap);
    }

    /// <summary>
    /// The note names the evidence rather than asserting a conclusion, so a reader can check it.
    /// </summary>
    [Fact]
    public void TheNoteNamesTheChallengeSurface()
    {
        var row = VendorWiring.Rows.Single(r => r.Vendor == "queue-it");

        Assert.Contains("Fetching Queue-it challenge", row.Note);
        Assert.Contains("Softblock", row.Note);
        Assert.Contains("BotDeflector", row.Note);
        Assert.Contains("queueitcaptcha", row.Note);
        Assert.Contains("X-queueit-challange", row.Note);
    }

    /// <summary>
    /// Nothing holds NotAChallenge any more. The value stays in the enum so the audit can show an empty state rather
    /// than have the taxonomy quietly shrink, and this pins the fact that it is empty.
    /// </summary>
    [Fact]
    public void NoRowUsesNotAChallengeAnyMore()
    {
        Assert.DoesNotContain(VendorWiring.Rows, r => r.State == VendorWiring.State.NotAChallenge);
    }
}
