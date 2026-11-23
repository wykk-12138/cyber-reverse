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

    private static readonly Regex Regular = new(
        "(?:const|static readonly)\\s+string\\s+(\\w+)\\s*=\\s*\"((?:[^\"\\\\]|\\\\.)*)\";",
        RegexOptions.Compiled);

    private static readonly Regex GqlHead = new(
        @"^\s*(?:mutation|query|fragment)\s+\w+",
        RegexOptions.Compiled);

    private static readonly Regex StrAndComment = new(
        "@\"(?:[^\"]|\"\")*\"|\"(?:[^\"\\\\]|\\\\.)*\"|//[^\\n]*|/\\*.*?\\*/",
        RegexOptions.Singleline | RegexOptions.Compiled);

    private static readonly Regex BareEllipsis = new(@"\.\.\.(?!\s*(?:[A-Za-z_]|on\b|\{))", RegexOptions.Compiled);

    private static string UnescapeRegular(string raw) =>
        Regex.Replace(raw, @"\\([""\\nrt])", m => m.Groups[1].Value switch
        {
            "\"" => "\"",
            "\\" => "\\",
            "n" => "\n",
            "r" => "\r",
            "t" => "\t",
            _ => m.Value,
        });

    /// <summary>The nearest ancestor that contains <c>src</c> and <c>docs</c>.</summary>
    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, "src", "Cybersole.Stores")))
            dir = dir.Parent;

        return dir?.FullName ?? string.Empty;
    }

    private static IEnumerable<(string File, string Name, string Body)> AllStringDocuments(int minLongLen)
    {
        var root = RepoRoot();
        if (string.IsNullOrEmpty(root)) yield break;

        foreach (var path in Directory.EnumerateFiles(Path.Combine(root, "src"), "*.cs", SearchOption.AllDirectories))
        {
            if (path.Contains(Path.DirectorySeparatorChar + "obj" + Path.DirectorySeparatorChar) ||
                path.Contains(Path.DirectorySeparatorChar + "bin" + Path.DirectorySeparatorChar))
                continue;

            var text = File.ReadAllText(path);
            var file = Path.GetFileName(path);

            foreach (Match match in Verbatim.Matches(text))
            {
                var body = match.Groups[2].Value.Replace("\"\"", "\"");
                var isShortGql = body.Length >= 40 && GqlHead.IsMatch(body);
                var isLongDoc = body.Length >= minLongLen &&
                    new[] { "mutation", "query", "fragment", "{" }.Any(s => body.Contains(s, StringComparison.Ordinal));
                if (isShortGql || isLongDoc)
                    yield return (file, match.Groups[1].Value, body);
            }

            foreach (Match match in Regular.Matches(text))
            {
                var body = UnescapeRegular(match.Groups[2].Value);
                var isShortGql = body.Length >= 40 && GqlHead.IsMatch(body);
                var isLongDoc = body.Length >= minLongLen &&
                    new[] { "mutation", "query", "fragment", "{" }.Any(s => body.Contains(s, StringComparison.Ordinal));
                if (isShortGql || isLongDoc)
                    yield return (file, match.Groups[1].Value, body);
            }
        }
    }

    public static IEnumerable<object[]> Constants()
    {
        foreach (var (file, name, body) in AllStringDocuments(200))
            yield return new object[] { file, name, body };
    }

    [Fact]
    public void TheScanFindsTheDocumentsItIsMeantToCheck()
    {
        // R1382: now scans both verbatim (@"...") and regular ("...") constants, including short (<200 char)
        // GraphQL documents, so StoreSessionQueries / ShopifyStorefrontQueries are no longer invisible to the guard.
        Assert.True(Constants().Count() >= 60, "the document scan found too few documents — check RepoRoot()");
    }

    [Theory]
    [MemberData(nameof(Constants))]
    public void EveryDocumentConstantIsWhole(string file, string name, string body)
    {
        Assert.DoesNotContain("chars total", body);
        Assert.DoesNotContain("TODO", body);
        Assert.DoesNotContain("FIXME", body);
        Assert.False(BareEllipsis.IsMatch(body), $"{file}:{name} carries a bare ellipsis");

        var fragment = (body.Length > 0 && (body[0] == ')' || body[0] == ',' || body[0] == '"'))
            || name.EndsWith("Prefix", StringComparison.Ordinal)
            || name.EndsWith("Suffix", StringComparison.Ordinal);
        if (fragment) return;

        Assert.Equal(body.Count(c => c == '{'), body.Count(c => c == '}'));
        Assert.Equal(0, body.Count(c => c == '"') % 2);
        Assert.EndsWith("}", body.TrimEnd());
    }

    /// <summary>
    /// A document with no caller is a document the replica cannot send.
    ///
    /// <para>
    /// R1382: strips string literals and comments before counting references so a constant like
    /// <c>WarhammerQueries.AddCreditCard</c> cannot match <c>"mutation AddCreditCard(..."</c> inside its own
    /// value. Also scans regular <c>"..."</c> constants alongside verbatim <c>@"..."</c> constants.
    /// </para>
    /// </summary>
    [Fact]
    public void EveryDocumentConstantHasAProductionCaller()
    {
        var allowed = AllowedWithoutCaller();
        var offenders = new List<string>();

        foreach (var (file, name, body) in DocumentConstants())
        {
            if (allowed.Contains(name)) continue;

            var uses = CountReferences(name) - 1;      // the declaration itself
            if (uses == 0) offenders.Add($"{file}:{name} ({body.Length} chars)");
        }

        Assert.True(offenders.Count == 0,
            "document constants nothing in src sends: " + string.Join(", ", offenders) +
            " — wire each to a step, or add it to AllowedWithoutCaller with a reason");
    }

    /// <summary>
    /// Documents kept on purpose without a caller yet (currently empty; <c>AddCreditCard</c> is wired into
    /// <c>WarhammerFlow.SubmitBillingAsync</c>).
    /// </summary>
    private static HashSet<string> AllowedWithoutCaller() => new(StringComparer.Ordinal);

    /// <summary>Every document-shaped constant in src: 60+ characters carrying a GraphQL or JSON signal.</summary>
    private static IEnumerable<(string File, string Name, string Body)> DocumentConstants() =>
        AllStringDocuments(60);

    /// <summary>How many times a name appears in actual C# code (excluding comments and string literals).</summary>
    private static int CountReferences(string name)
    {
        var root = RepoRoot();
        if (string.IsNullOrEmpty(root)) return 0;

        var pattern = new Regex("\\b" + Regex.Escape(name) + "\\b", RegexOptions.Compiled);
        var total = 0;
        foreach (var path in Directory.EnumerateFiles(Path.Combine(root, "src"), "*.cs", SearchOption.AllDirectories))
        {
            if (path.Contains(Path.DirectorySeparatorChar + "obj" + Path.DirectorySeparatorChar) ||
                path.Contains(Path.DirectorySeparatorChar + "bin" + Path.DirectorySeparatorChar))
                continue;
            var codeOnly = StrAndComment.Replace(File.ReadAllText(path), " ");
            total += pattern.Matches(codeOnly).Count;
        }

        return total;
    }
}
