using System;
using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1260: the restock cadence, reconstructed from the two field names the image carries
/// (<c>RestockInterval _lastRestockPing</c> at 0x1433A28C7) rather than from a guessed timer.
/// </summary>
public sealed class RestockGateTests
{
    private static RestockGate Gate(TimeSpan interval, DateTime now)
    {
        var gate = new RestockGate(interval, () => now);
        return gate;
    }

    [Fact]
    public void TheFirstCheckIsDue()
    {
        Assert.True(Gate(TimeSpan.FromSeconds(30), DateTime.UnixEpoch).IsDue);
        Assert.Null(Gate(TimeSpan.FromSeconds(30), DateTime.UnixEpoch).LastRestockPing);
    }

    [Fact]
    public void TheIntervalGatesTheNextCheck()
    {
        var now = DateTime.UnixEpoch;
        var gate = new RestockGate(TimeSpan.FromSeconds(30), () => now);
        gate.MarkPinged();
        Assert.False(gate.IsDue);

        now = now.AddSeconds(29);
        Assert.False(gate.IsDue);

        now = now.AddSeconds(1);
        Assert.True(gate.IsDue);
    }

    [Fact]
    public void MarkingWithoutPingingDoesNotAdvanceTheClock()
    {
        // IsDue is read-only: a caller that checks and then fails must not lose its window
        var now = DateTime.UnixEpoch;
        var gate = new RestockGate(TimeSpan.FromSeconds(10), () => now);
        Assert.True(gate.IsDue);
        Assert.True(gate.IsDue);
        Assert.Null(gate.LastRestockPing);
    }

    [Fact]
    public void ANonPositiveIntervalIsRejected()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() => new RestockGate(TimeSpan.Zero));
        Assert.Throws<ArgumentOutOfRangeException>(() => new RestockGate(TimeSpan.FromSeconds(-1)));
    }

    [Fact]
    public void TheIntervalIsReadableAsTheImageNamesIt()
    {
        var gate = new RestockGate(TimeSpan.FromSeconds(15), () => DateTime.UnixEpoch);
        Assert.Equal(TimeSpan.FromSeconds(15), gate.RestockInterval);
    }
}
