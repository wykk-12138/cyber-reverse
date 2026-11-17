using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// PollQueueAsync, which used to be a bare Ok and now makes the decision QueueItProtocol describes.
///
/// <para>
/// R960. The step returned success without looking at anything, so a flow that hit a waiting room believed it had passed
/// one. The replacement polls until the deadline, waits while the pass's remaining validity is under the margin, and
/// returns a retryable failure when time runs out -- because out of time is not success, and neither is a pass too short to
/// spend.
/// </para>
/// </summary>
public class PollQueueWiringTests
{
    /// <summary>The step is no longer a constant-time Ok, and it names the protocol it now asks.</summary>
    [Fact]
    public void TheStepUsesTheProtocol()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));

        Assert.DoesNotContain("Task<StepOutcome> PollQueueAsync(FlowContext c, CancellationToken ct) => Ok();", doc);

        Assert.Contains("QueueItProtocol.IsQueueHost", doc);
        Assert.Contains("QueueItProtocol.Verdict", doc);
        Assert.Contains("QueueItProtocol.IsUsable", doc);
        Assert.Contains("QueueItProtocol.Describe", doc);
    }

    /// <summary>
    /// Running out of time is a retryable failure. The bare Ok said success, which was the lie being removed.
    /// </summary>
    [Fact]
    public void RunningOutOfTimeFails()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));

        Assert.Contains("queue not passed within the deadline", doc);
        Assert.Contains("retryable: true", doc);

        // and the reason is recorded where the code is
        Assert.Contains("out of time is a retryable failure, not a success", doc);
    }

    /// <summary>
    /// A short pass does not end the wait -- it keeps polling rather than spending the pass on a request that will be
    /// refused.
    /// </summary>
    [Fact]
    public void AShortPassKeepsWaiting()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));

        Assert.Contains("short pass: keep waiting rather than spend it", doc);
        Assert.Contains("queueMinRemaining", doc);
    }

    /// <summary>A non-queue surface returns success immediately, because there is nothing to wait for.</summary>
    [Fact]
    public void ANonQueueSurfacePassesStraightThrough()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));

        Assert.Contains("not a queue surface, nothing to wait for", doc);
    }

    /// <summary>The three settings the loop reads are the ones the image's field names imply.</summary>
    [Fact]
    public void TheThreeSettingsAreNamed()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));

        Assert.Contains("queueTimeout", doc);
        Assert.Contains("queuePollMs", doc);
        Assert.Contains("queuePassSeconds", doc);
    }

    /// <summary>And the protocol's classification is what the loop's switch branches on, not a status range.</summary>
    [Fact]
    public void TheBranchesAreVerdictsNotStatuses()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));

        foreach (var verdict in new[] { "QueueVerdict.Passed", "QueueVerdict.Banned", "QueueVerdict.RetryLater", "QueueVerdict.Failed" })
            Assert.Contains(verdict, doc);
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