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
///
/// <para>
/// R1077 sharpened the second fact: the decompile showed the transport is server-delivered (connect/app's
/// ConfigAdded sync) rather than merely "not known here", so the steps now name that channel and the
/// credential it needs. The guard follows the fact it protects -- the wording below changed with it.
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
    /// And the steps say what is actually missing -- the server-delivered config schema, naming the
    /// channel (connect/app) and the credential it needs rather than the store. The fourth assertion
    /// pins one message whole: the short phrases appear in every step's message, so only a
    /// full-message assertion can be killed by a single-line mutation.
    /// </summary>
    /// <summary>
    /// R1295: the classification has to be on <em>each</em> message, not somewhere in the file.
    ///
    /// <para>
    /// The file-wide assertion below passed even after one message was emptied, because the other six still mention
    /// server-delivered and the credential. This one reads the line that names the step and requires the four phrases
    /// there, which is what a regression would actually remove.
    /// </para>
    /// </summary>
    [Theory]
    [InlineData("product")]
    [InlineData("add-to-cart")]
    [InlineData("basket")]
    [InlineData("checkout")]
    [InlineData("shipping")]
    [InlineData("payment")]
    [InlineData("place-order")]
    public void EachStepCarriesTheReasonItself(string step)
    {
        var line = Source()
            .Split('\n')
            .FirstOrDefault(l => l.Contains("farfetch: " + step + " ", StringComparison.Ordinal));

        Assert.NotNull(line);
        Assert.Contains("route unrecorded locally", line, StringComparison.Ordinal);
        Assert.Contains("server-delivered", line, StringComparison.Ordinal);
        Assert.Contains("connect/app", line, StringComparison.Ordinal);
        Assert.Contains("schema needs the original login", line, StringComparison.Ordinal);
    }

    [Fact]
    public void TheStepsNameTheServerDeliveredTransport()
    {
        var source = Source();
        Assert.Contains("server-delivered", source, StringComparison.Ordinal);
        Assert.Contains("connect/app", source, StringComparison.Ordinal);
        Assert.Contains("schema needs the original login", source, StringComparison.Ordinal);
        // R1294: the message was reclassified from "endpoint unknown" to "route unrecorded locally" because
        // R1077 had already closed the question. The assertion follows the fact, not the sentence.
        Assert.Contains("route unrecorded locally", source, StringComparison.Ordinal);
    }
}
