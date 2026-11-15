using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// Cybersole's own service hosts, read whole in R138 — fifteen of them, every one a literal.
///
/// <code>
/// amazon-waf.cybersole.io      a WAF solver
/// analytics.cybersole.io       telemetry of the analytics page
/// api.cybersole.io             the backend — licences, tasks, solver calls
/// castle.cybersole.io          Castle (device fingerprint vendor)
/// cdn.cybersole.io             static assets
/// cf-solver.cybersole.io       Cloudflare solver
/// datadome.cybersole.io        DataDome relay (recorded in R101)
/// forward.cybersole.io         request forwarding
/// images.cybersole.io          images
/// match.cybersole.io           ?
/// pop4.cybersole.io            ?
/// proxy.cybersole.io           proxy service
/// support.cybersole.io         support
/// telemetry.cybersole.io       telemetry
/// text-captcha.cybersole.io    text captcha solver
/// </code>
///
/// <para>
/// <b>There is no <c>kasada.cybersole.io</c>.</b> The Kasada strategy of R136/R137 has an
/// <c>Api</c> road whose address the strings never name, and the host list settles where it is not:
/// whatever serves that road is not a dedicated Kasada host. <c>api.cybersole.io</c> is the remaining
/// candidate, and the status string <c>Kasada API down (Contact staff)</c> fits it — "contact staff"
/// is what an operator says when <b>their own</b> backend is down, not a third party's. That is an
/// inference, not a capture, and it is recorded as one.
/// </para>
///
/// <para>
/// The same pool carries the solver registry the Settings page shows:
/// <c>CloudflareSolvers</c>, <c>CloudflareSolverId</c>, <c>CloudflareSolver.Default</c>,
/// <c>CapSolver</c>, <c>CloseSolver</c>, and the message
/// <c>Cloudflare solver refused the token, solving in-bot</c> — which is the same
/// local-versus-service split the Kasada strategy has.
/// </para>
/// </summary>
public static class CybersoleHosts
{
    /// <summary>Every <c>*.cybersole.io</c> host the image names, in the pool's order.</summary>
    public static readonly IReadOnlyList<string> All = new[]
    {
        "amazon-waf.cybersole.io",
        "analytics.cybersole.io",
        "api.cybersole.io",
        "castle.cybersole.io",
        "cdn.cybersole.io",
        "cf-solver.cybersole.io",
        "datadome.cybersole.io",
        "forward.cybersole.io",
        "images.cybersole.io",
        "match.cybersole.io",
        "pop4.cybersole.io",
        "proxy.cybersole.io",
        "support.cybersole.io",
        "telemetry.cybersole.io",
        "text-captcha.cybersole.io",
    };

    /// <summary>The solver hosts, by the wall they solve.</summary>
    public static readonly IReadOnlyDictionary<string, string> SolverHosts =
        new Dictionary<string, string>(System.StringComparer.Ordinal)
        {
            ["amazon-waf.cybersole.io"] = "Amazon WAF",
            ["cf-solver.cybersole.io"] = "Cloudflare",
            ["datadome.cybersole.io"] = "DataDome",
            ["text-captcha.cybersole.io"] = "text captcha",
        };

    /// <summary>
    /// Where the Kasada <c>Api</c> road most plausibly points. <b>Inferred, not captured</b>: the host
    /// list has no Kasada-specific entry, and <c>api.cybersole.io</c> is the backend the operator
    /// message refers to.
    /// </summary>
    public const string KasadaApiCandidate = "api.cybersole.io";

    /// <summary>The inference, written down so it is never mistaken for a capture.</summary>
    public const string KasadaApiEvidence =
        "no kasada.cybersole.io exists; api.cybersole.io is the only remaining candidate; " +
        "inferred from 'Kasada API down (Contact staff)', no capture";

    /// <summary>The solver-registry names the Settings page needs.</summary>
    public static readonly IReadOnlyList<string> SolverRegistryNames = new[]
    {
        "CloudflareSolvers", "CloudflareSolverId", "CloudflareSolver.Default",
        "CapSolver", "CloseSolver", "EmptySolver.html",
    };

    /// <summary>The message that proves the Cloudflare path has the same split.</summary>
    public const string CloudflareInBotFallback =
        "Cloudflare solver refused the token, solving in-bot";

    /// <summary>True when the host is one of the fifteen.</summary>
    public static bool IsKnown(string? host) =>
        !string.IsNullOrEmpty(host) && All.Contains(host, System.StringComparer.Ordinal);

    /// <summary>True when the host exists to solve a wall.</summary>
    public static bool IsSolverHost(string? host) =>
        !string.IsNullOrEmpty(host) && SolverHosts.ContainsKey(host);

    /// <summary>The wall a solver host solves, or null for a non-solver host.</summary>
    public static string? WallFor(string? host) =>
        string.IsNullOrEmpty(host) ? null
            : SolverHosts.TryGetValue(host, out var wall) ? wall : null;
}
