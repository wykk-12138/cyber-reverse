using System;
using System.IO;
using System.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1034: the endpoint ledgers did not know about each other, and the tool's comparison could not see a templated
/// path at all.
///
/// <para>
/// Two files record unbacked endpoints. <c>EndpointEvidenceRatchetTests</c> holds the ratchet, and
/// <c>docs/ENDPOINT_PROVENANCE.md</c> is what <c>tools/endpoint-provenance.py</c> reads. Neither referenced the other,
/// so a round spent adding entries to one changed nothing in the other's count -- which is how R1033 ended with six
/// new ledger rows and the tool still reporting twelve.
/// </para>
///
/// <para>
/// The deeper defect was in the tool. Its scanner reports a templated path as a prefix plus "{...}" while the ledger
/// stores the literal in full, so a path containing a template could never match however carefully it was registered.
/// Both spellings are now accepted. These guards pin the cross-references and the class that was missing.
/// </para>
/// </summary>
public sealed class EndpointLedgerLinkTests
{
    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }

    private static string Ledger() =>
        File.ReadAllText(Path.Combine(Root(), "docs", "ENDPOINT_PROVENANCE.md"));

    /// <summary>The tool's ledger names the ratchet, so a reader of one is told the other exists.</summary>
    [Fact]
    public void TheProvenanceLedgerNamesTheRatchet()
    {
        Assert.Contains("EndpointEvidenceRatchetTests", Ledger(), StringComparison.Ordinal);
    }

    /// <summary>And the ratchet names the ledger.</summary>
    [Fact]
    public void TheRatchetNamesTheProvenanceLedger()
    {
        var text = File.ReadAllText(
            Path.Combine(Root(), "tests", "Cybersole.Tests", "EndpointEvidenceRatchetTests.cs"));

        Assert.Contains("ENDPOINT_PROVENANCE", text, StringComparison.Ordinal);
    }

    /// <summary>
    /// The ledger carries the fifth class. `sent` means the replica really makes this request, the image names no such
    /// route, and there is no live response to cite -- which is neither a fixture nor something still undecided.
    /// </summary>
    [Fact]
    public void TheLedgerHasTheSentClass()
    {
        var body = Ledger();
        Assert.Contains("## sent", body, StringComparison.Ordinal);

        var sent = body.Split('\n').Count(l => l.TrimStart().StartsWith("- `sent`", StringComparison.Ordinal));
        Assert.True(sent >= 6, "expected at least six sent entries, saw " + sent);
    }

    /// <summary>
    /// Every path the ledger files as `sent` also appears in the ratchet's own recorded set, or the two disagree about
    /// what exists.
    /// </summary>
    [Fact]
    public void EverySentPathIsKnownToTheRatchet()
    {
        var ledger = Ledger();
        var ratchet = File.ReadAllText(
            Path.Combine(Root(), "tests", "Cybersole.Tests", "EndpointEvidenceRatchetTests.cs"));

        var sentPaths = ledger.Split('\n')
            .Select(l => l.Trim())
            .Where(l => l.StartsWith("- `sent`", StringComparison.Ordinal))
            .Select(l => l.Split('`')[3])
            .ToList();

        Assert.NotEmpty(sentPaths);
        foreach (var path in sentPaths)
            Assert.Contains(path, ratchet, StringComparison.Ordinal);
    }
}
