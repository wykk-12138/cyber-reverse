using System.Text.RegularExpressions;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// How many store-flow step overrides do nothing but return an outcome.
///
/// <para>
/// R986. Priority one is that each store can actually check out, and the figure that had been quoted for it was "every
/// audited step has at least one override". That is a different claim: a step having an override somewhere says nothing
/// about whether a given store's override does anything. Measuring per file gives 185 overrides of which 180 do work.
/// </para>
///
/// <para>
/// The first classifier written for this counted only an await, an HTTP call or session access as work, and thereby called
/// <c>=&gt; OpenCheckoutAsync(c, "goat-checkout", "/checkout", ct)</c> a placeholder -- five false positives. That is the
/// mistake R824 recorded about delegation: a call to a method of the same class has no receiver, so any pattern looking for
/// <c>something.Name</c> misses it. Counting delegation as work brings the figure to five, of which four are Bstn's order
/// chain and one is Shopify's deliberately empty GetCsrf.
/// </para>
///
/// <para>
/// This pins the count. A placeholder is not automatically a gap -- a step may genuinely not apply to a store -- so the
/// assertion is an upper bound plus a shape check: the only flow allowed to be mostly placeholders is the one whose
/// messages name an unknown endpoint.
/// </para>
/// </summary>
[Collection("external-tools")]
public class FlowWorkAuditTests
{
    /// <summary>Placeholder overrides measured at R986. May only fall, and a lowering edit should say what changed.</summary>
    private const int KnownPlaceholders = 5;

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;
        Assert.True(dir is not null, "could not locate the repository root from " + AppContext.BaseDirectory);
        return dir!.FullName;
    }

    private static string FlowsDir() => Path.Combine(RepoRoot(), "src", "Cybersole.Stores", "Flows");

    private static readonly Regex Override = new(
        @"public\s+override\s+(?:async\s+)?Task<StepOutcome>\s+(\w+)\s*Async\s*\([^)]*\)\s*"
        + @"(\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}|\s*=>[^;]*;)",
        RegexOptions.Singleline | RegexOptions.Compiled);

    private static readonly Regex Outcome = new(@"StepOutcome\.(?:Fail|Stop|Success)\s*\([^;]*?\)",
        RegexOptions.Singleline | RegexOptions.Compiled);

    private static readonly Regex Work = new(@"\bawait\b|\bHttp\b|\bc\.Session\b|\bc\.Vars\b|\bthrow\b",
        RegexOptions.Compiled);

    private static readonly Regex Delegation = new(@"\b\w*Async\s*\(|\b\w+Core\s*\(|\bOpen\w*\s*\(", RegexOptions.Compiled);

    private static bool DoesWork(string body)
    {
        var rest = Outcome.Replace(body, string.Empty);
        return Work.IsMatch(rest) || Delegation.IsMatch(rest);
    }

    private static List<(string Flow, string Step)> Placeholders()
    {
        var found = new List<(string, string)>();

        foreach (var path in Directory.EnumerateFiles(FlowsDir(), "*Flow.cs", SearchOption.TopDirectoryOnly))
        {
            var text = File.ReadAllText(path);
            var flow = Path.GetFileName(path)[..^"Flow.cs".Length];

            foreach (Match m in Override.Matches(text))
            {
                if (!DoesWork(m.Groups[2].Value)) found.Add((flow, m.Groups[1].Value));
            }
        }

        return found;
    }

    [Fact]
    public void MostOverridesDoWork()
    {
        var overrides = 0;
        foreach (var path in Directory.EnumerateFiles(FlowsDir(), "*Flow.cs", SearchOption.TopDirectoryOnly))
            overrides += Override.Matches(File.ReadAllText(path)).Count;

        Assert.True(overrides > 100, $"only {overrides} overrides found -- the signature pattern may have stopped matching");

        var placeholders = Placeholders().Count;
        Assert.True(placeholders <= KnownPlaceholders,
            $"{placeholders} overrides do nothing but return an outcome, up from {KnownPlaceholders}:"
            + Environment.NewLine + string.Join(Environment.NewLine,
                Placeholders().Select(p => p.Flow + "." + p.Step)));
    }

    /// <summary>
    /// The one flow allowed to be mostly placeholders is the one whose messages say the endpoint is unknown. A store that
    /// silently returns failures without saying why would look identical in the counts above.
    /// </summary>
    [Fact]
    public void AFlowWithPlaceholdersSaysWhy()
    {
        var byFlow = Placeholders().GroupBy(p => p.Flow).ToDictionary(g => g.Key, g => g.Count());

        foreach (var (flow, count) in byFlow)
        {
            if (count < 2) continue;      // a single one is the deliberate no-op case, which carries its reason in a comment

            var text = File.ReadAllText(Path.Combine(FlowsDir(), flow + "Flow.cs"));
            Assert.True(text.Contains("endpoint unknown", StringComparison.OrdinalIgnoreCase),
                $"{flow} has {count} placeholder overrides and never says why; a placeholder that does not name what is "
                + "missing reads as an oversight rather than a recorded gap");
        }
    }
}