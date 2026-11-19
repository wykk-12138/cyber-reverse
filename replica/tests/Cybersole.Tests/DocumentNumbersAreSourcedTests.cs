using System;
using System.Collections.Generic;
using System.IO;
using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R1197: a document that quotes a function count has to say where it came from.
///
/// <para>
/// Criterion (e) ends with "every number in the documents comes from METRICS.md", and two documents were not
/// doing it: <c>PARITY_PRODUCT.md</c> carried a table measured at some earlier point and <c>PARITY_CLAIMS.md</c>'s
/// C6 row quoted a replica total from R707, both written as if current. Nothing was wrong with either measurement
/// - they used <c>idautils.Functions()</c> while METRICS counts <c>.pdata</c>, two different populations - so the
/// fix was not to change the numbers but to make each one travel with its date and its basis.
/// </para>
///
/// <para>
/// This guard scans the live documents for two-group numbers such as <c>179,456</c> and requires the same line to
/// name a source: METRICS, a snapshot word, or the round that measured it. Logs are excluded - a ledger entry is
/// dated by its own heading and is supposed to record what a round saw.
/// </para>
/// </summary>
[Collection("external-tools")]
public sealed class DocumentNumbersAreSourcedTests
{
    /// <summary>
    /// The documents whose job is to state where the project stands, and therefore must date their numbers.
    /// <c>PARITY_PRODUCT.md</c> is deliberately not here: it is a measurement dossier of roughly eleven hundred
    /// lines, and rather than repeat "时点" on every row its table now carries a header saying it is a snapshot and
    /// pointing at METRICS for current values - which is what this guard would otherwise be enforcing row by row.
    /// </summary>
    private static readonly string[] LiveDocs =
    {
        "docs/PARITY_CLAIMS.md",
        "docs/GOAL.md",
    };

    // exactly two groups, and not part of a longer number: `51,694,952` contains the substring `694,952`.
    private static readonly Regex Number = new(@"(?<![\d,])\d{1,3},\d{3}(?![\d,])", RegexOptions.Compiled);

    // R1197: a two-group number is not necessarily a function count - section sizes and byte totals look exactly
    // the same (`998,520`, `309,404`). Only lines that talk about functions are held to the sourcing rule, which
    // is the rule criterion (e) actually states.
    private static readonly Regex AboutFunctions = new(@"函数|function", RegexOptions.IgnoreCase | RegexOptions.Compiled);
    private static readonly Regex Source = new(@"METRICS|时点|snapshot|R\d{3,4}|\d{4}-\d{2}-\d{2}", RegexOptions.Compiled);

    private readonly ITestOutputHelper _out;

    public DocumentNumbersAreSourcedTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void EveryQuotedFunctionCountNamesItsSource()
    {
        var root = FindRepoRoot();
        var offenders = new List<string>();

        foreach (var rel in LiveDocs)
        {
            var path = Path.Combine(root, rel.Replace('/', Path.DirectorySeparatorChar));
            if (!File.Exists(path)) continue;
            var lines = File.ReadAllLines(path);
            for (var i = 0; i < lines.Length; i++)
            {
                var line = lines[i];
                if (!Number.IsMatch(line)) continue;
                if (!AboutFunctions.IsMatch(line)) continue;
                if (Source.IsMatch(line)) continue;
                offenders.Add($"{rel}:{i + 1}: {line.Trim()}");
            }
        }

        foreach (var o in offenders) _out.WriteLine(o);
        Assert.Empty(offenders);
    }

    private static string FindRepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, "replica")))
            dir = dir.Parent;
        if (dir is null) throw new InvalidOperationException("repository root not found");
        return dir.FullName;
    }
}
