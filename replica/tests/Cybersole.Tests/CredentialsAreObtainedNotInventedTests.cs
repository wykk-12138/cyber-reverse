using System.Text.RegularExpressions;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// A credential the replica holds must have been obtained, not invented.
///
/// <para>
/// R991. <c>GetPaymentTokenAsync</c> used to assign <c>"tok_" + Guid.NewGuid()...</c> and return success when no token was
/// already present. The comment on Shopify's <c>GetCsrf</c> states the rule that forbids it, with round 823's reasoning:
/// a token the server never issued makes every request carrying it invalid, so the failure does not disappear, it moves
/// to whichever call happens to send the value and arrives there disguised as a rejection from the store. A fabricated
/// credential also hides which step was missing, which is the part that costs rounds.
/// </para>
///
/// <para>
/// The fabrication almost never ran -- Footsites, Magento and Shopify each read a real token out of their own tokenise
/// response and <c>Gateways.cs</c> mints four kinds through real endpoints -- so removing it cost nothing and the full
/// suite stayed green. This guard exists because "almost never runs" is exactly the condition under which a defect
/// survives: nothing exercises it, nothing fails, and the next person reads it as intended behaviour.
/// </para>
/// </summary>
public class CredentialsAreObtainedNotInventedTests
{
    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;
        Assert.True(dir is not null, "could not locate the repository root from " + AppContext.BaseDirectory);
        return dir!.FullName;
    }

    /// <summary>
    /// Token-ish members assigned a freshly generated value. Deliberately narrow: session ids, correlation ids and
    /// anti-forgery values legitimately come from a CSPRNG, so only names that name a credential the server must issue are
    /// covered, and <c>Gateways.cs</c>'s nonce minting is included because those nonces go to the gateway that accepts
    /// them rather than to a store that never saw them.
    ///
    /// <para>
    /// R992 widened this to session variables. The first version matched only <c>Token =</c> assignments to a field, which
    /// is why it passed while <c>GetTokenAsync</c> was storing sixteen random bytes under <c>Vars["token"]</c> -- a session
    /// variable named like a credential, invisible to a pattern that expected an identifier on the left. Same lesson as
    /// the delegation bug in flow_work_audit: the shape I expected was not the only shape it takes.
    /// </para>
    /// </summary>
    private static readonly Regex Invented = new(
        @"(\b\w*(PaymentToken|AuthToken|AccessToken|CsrfToken|SessionToken)\w*\s*=\s*[^;]*\b(Guid\.NewGuid|RandomNumberGenerator)\b"
        + @"|Vars\[\s*""[^""]*(token|nonce|secret|credential)[^""]*""\s*\]\s*=[^;]*\b(RandomNumberGenerator|Guid\.NewGuid)\b)",
        RegexOptions.Compiled | RegexOptions.IgnoreCase);

    [Fact]
    public void NoCredentialIsMintedLocally()
    {
        var offenders = new List<string>();
        var src = Path.Combine(RepoRoot(), "src");

        foreach (var path in Directory.EnumerateFiles(src, "*.cs", SearchOption.AllDirectories))
        {
            if (path.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}") ||
                path.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}"))
                continue;

            var lines = File.ReadAllLines(path);
            for (var i = 0; i < lines.Length; i++)
            {
                if (Invented.IsMatch(lines[i]))
                    offenders.Add($"{Path.GetFileName(path)}:{i + 1}  {lines[i].Trim()}");
            }
        }

        Assert.True(offenders.Count == 0,
            "a credential is being generated locally instead of obtained. A value the server never issued makes every "
            + "request carrying it invalid, and the failure surfaces somewhere else:"
            + Environment.NewLine + string.Join(Environment.NewLine, offenders));
    }

    /// <summary>
    /// The step that once fabricated a token must still exist and must still short-circuit on a real one -- removing the
    /// fabrication by deleting the step would hide the gap instead of reporting it.
    /// </summary>
    [Fact]
    public void TheFallbackReportsRatherThanInvends()
    {
        var text = File.ReadAllText(Path.Combine(RepoRoot(), "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));

        Assert.Contains("Task<StepOutcome> GetPaymentTokenAsync", text, StringComparison.Ordinal);
        Assert.Contains("if (!string.IsNullOrEmpty(c.Session.PaymentToken)) return StepOutcome.Success();",
            text, StringComparison.Ordinal);
        Assert.Contains("will not invent one", text, StringComparison.Ordinal);
    }

    /// <summary>
    /// The generic token step carries the same rule as the payment one, and for a sharper reason: <c>GetAuthTokenAsync</c>
    /// delegates here and says it acquires an authorisation token, which only the server can issue.
    /// </summary>
    [Fact]
    public void TheGenericTokenStepAlsoReports()
    {
        var text = File.ReadAllText(Path.Combine(RepoRoot(), "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));

        Assert.Contains("Task<StepOutcome> GetTokenAsync", text, StringComparison.Ordinal);
        Assert.Contains("not invent a credential", text, StringComparison.Ordinal);
        Assert.DoesNotContain("Vars[\"token\"] = token", text, StringComparison.Ordinal);
    }
}