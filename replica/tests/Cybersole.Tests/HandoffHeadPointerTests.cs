using System.Text.RegularExpressions;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// docs/HANDOFF.md opens with a "where we are now" block that a new session reads first, and the numbers in it must not be
/// typed by hand.
///
/// <para>
/// R979. That block was found dated R826 -- a hundred and fifty rounds behind -- quoting a suite total and two metric
/// figures that no longer matched, and citing as evidence for criterion (d) a check that turned out to cover five rows of
/// twenty-two. A live block holding dead numbers is worse than no block, because it is read first and believed. The
/// project rule already said numbers live only in docs/METRICS.md; nothing enforced it for this file.
/// </para>
///
/// <para>
/// So this asserts the two properties that were violated: the block points at the single source, and it does not restate a
/// current metric value. It deliberately says nothing about the append-only history below, where numbers are correct as
/// history and quoting them is the point.
/// </para>
/// </summary>
public class HandoffHeadPointerTests
{
    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "AGENTS.md")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }

    /// <summary>Everything before the history marker is the live block; everything after is a per-round record.</summary>
    private static string Head()
    {
        var text = File.ReadAllText(Path.Combine(RepoRoot(), "docs", "HANDOFF.md"));
        var cut = text.IndexOf("# 历史", StringComparison.Ordinal);
        Assert.True(cut > 0, "docs/HANDOFF.md no longer has a '# 历史' marker, so the live block cannot be delimited");
        return text[..cut];
    }

    /// <summary>The whole numbers METRICS.md currently reports, so the check follows the source rather than a list.</summary>
    private static List<string> MetricValues()
    {
        var values = new List<string>();
        foreach (var line in File.ReadAllLines(Path.Combine(RepoRoot(), "docs", "METRICS.md")))
        {
            if (!line.StartsWith("|", StringComparison.Ordinal)) continue;
            var cells = line.Trim().Trim('|').Split('|');
            if (cells.Length < 2) continue;

            var value = cells[1].Trim();
            if (!Regex.IsMatch(value, @"^[\d,]+$")) continue;
            if (int.TryParse(value.Replace(",", ""), out var n) && n > 100) values.Add(value);
        }

        return values;
    }

    [Fact]
    public void TheLiveBlockPointsAtTheSingleSourceOfNumbers()
    {
        Assert.Contains("METRICS.md", Head(), StringComparison.Ordinal);
    }

    [Fact]
    public void TheLiveBlockRestatesNoCurrentMetricValue()
    {
        var head = Head().Split('\n');
        var offenders = new List<string>();

        foreach (var value in MetricValues())
        {
            // a number bounded by non-digits on both sides: "173,952" must not match inside "1,173,952", and a round label
            // like "R951" must not be read as the number 951
            var pattern = $@"(?<![0-9A-Za-z_,]){Regex.Escape(value)}(?![0-9])";

            for (var i = 0; i < head.Length; i++)
            {
                if (!Regex.IsMatch(head[i], pattern)) continue;
                if (head[i].Contains("METRICS", StringComparison.Ordinal)) continue;   // a pointer on the same line is fine
                offenders.Add($"L{i + 1}: {value} -- {head[i].Trim()}");
            }
        }

        Assert.True(offenders.Count == 0,
            "the live block restates current metric values; replace them with a pointer to docs/METRICS.md:"
            + Environment.NewLine + string.Join(Environment.NewLine, offenders));
    }
}