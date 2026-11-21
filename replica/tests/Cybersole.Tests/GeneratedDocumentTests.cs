using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Every document-shaped string constant in <c>src</c> has to be a whole document.
///
/// <para>
/// R1326 found <c>WarhammerQueries.ApproveOnboardPaymentMutation</c> shipping with the literal text
/// "[4040 chars total]" at its end — a truncation notice pasted out of a display, which left the document
/// stopping in the middle and the flow sending a malformed query. The one-class reflection guard added then
/// covered that class only; this covers the repository, because the mistake is about how documents get into
/// the source, not about which class they live in.
/// </para>
///
/// <para>
/// Four signals, and two exemptions that this test only grants where the constant says so in its own text:
/// a constant that begins with the tail of an operation header (<c>)</c>, <c>,</c> or <c>"</c>) is a fragment
/// whose header the caller supplies, so its braces are expected to be unbalanced. Everything else must
/// balance, must end with <c>}</c>, and must carry no truncation marker.
/// </para>
/// </summary>
public sealed class GeneratedDocumentTests
{
    private static readonly Regex Verbatim = new(
        "(?:const|static readonly)\\s+string\\s+(\\w+)\\s*=\\s*@\"((?:[^\"]|\"\")*)\";",
        RegexOptions.Singleline | RegexOptions.Compiled);

    private static readonly Regex BareEllipsis = new(@"\.\.\.(?!\s*(?:[A-Za-z_]|on\b|\{))", RegexOptions.Compiled);

    /// <summary>The nearest ancestor that contains <c>src</c> and <c>docs</c>.</summary>
    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, "src", "Cybersole.Stores")))
            dir = dir.Parent;

        return dir?.FullName ?? string.Empty;
    }

    public static IEnumerable<object[]> Constants()
    {
        var root = RepoRoot();
        if (string.IsNullOrEmpty(root)) yield break;

        foreach (var path in Directory.EnumerateFiles(Path.Combine(root, "src"), "*.cs", SearchOption.AllDirectories))
        {
            if (path.Contains(Path.DirectorySeparatorChar + "obj" + Path.DirectorySeparatorChar) ||
                path.Contains(Path.DirectorySeparatorChar + "bin" + Path.DirectorySeparatorChar))
                continue;

            var text = File.ReadAllText(path);
            foreach (Match match in Verbatim.Matches(text))
            {
                var body = match.Groups[2].Value.Replace("\"\"", "\"");
                if (body.Length < 200) continue;
                if (!new[] { "mutation", "query", "fragment", "{" }.Any(s => body.Contains(s, StringComparison.Ordinal)))
                    continue;

                yield return new object[] { Path.GetFileName(path), match.Groups[1].Value, body };
            }
        }
    }

    [Fact]
    public void TheScanFindsTheDocumentsItIsMeantToCheck()
    {
        // A scan that silently finds nothing passes every assertion below it, so the population is asserted
        // first. Fourteen was the count when this was written.
        Assert.True(Constants().Count() >= 10, "the document scan found almost nothing — check RepoRoot()");
    }

    [Theory]
    [MemberData(nameof(Constants))]
    public void EveryDocumentConstantIsWhole(string file, string name, string body)
    {
        Assert.DoesNotContain("chars total", body);
        Assert.DoesNotContain("TODO", body);
        Assert.DoesNotContain("FIXME", body);
        Assert.False(BareEllipsis.IsMatch(body), $"{file}:{name} carries a bare ellipsis");

        var fragment = body.Length > 0 && (body[0] == ')' || body[0] == ',' || body[0] == '"');
        if (fragment) return;

        Assert.Equal(body.Count(c => c == '{'), body.Count(c => c == '}'));
        Assert.Equal(0, body.Count(c => c == '"') % 2);
        Assert.EndsWith("}", body.TrimEnd());
    }
}
