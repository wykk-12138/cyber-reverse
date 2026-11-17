using System;
using System.IO;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1038 retracts R1036. That round found farfetch.com at zero, concluded the original never mentions the store, and
/// turned all seven steps into reports on that basis. A bare-word probe shows the conclusion was wrong: "Farfetch"
/// appears twice and "Farfetch Checkout" once, so the original does have a checkout flow for this store.
///
/// <para>
/// What is missing is this workspace's knowledge of the transport, not the store. Farfetch is covered by the original
/// and uncovered here, which is a different thing from being an addition.
/// </para>
///
/// <para>
/// These guards assert the two facts that matter and nothing about phrasing. An earlier draft also forbade the file
/// from quoting R1036's retracted sentence, which made it impossible to write the retraction down -- a guard can be too
/// strict in a way that fights the comment it is protecting.
/// </para>
/// </summary>
public sealed class FarfetchIsCoveredByTheOriginalTests
{
    private static string Source() =>
        File.ReadAllText(Path.Combine(
            FindRoot(), "src", "Cybersole.Stores", "Flows", "FarfetchFlow.cs"));

    private static string FindRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }

    /// <summary>The evidence for the retraction is named where the reader will meet it.</summary>
    [Fact]
    public void TheCommentNamesTheEvidence()
    {
        Assert.Contains("Farfetch Checkout", Source(), StringComparison.Ordinal);
    }

    /// <summary>
    /// And the steps say what is actually missing -- the transport -- rather than that the store does not exist.
    /// </summary>
    [Fact]
    public void TheStepsNameTheUnknownTransport()
    {
        var source = Source();
        Assert.Contains("does not know its transport", source, StringComparison.Ordinal);
    }
}
