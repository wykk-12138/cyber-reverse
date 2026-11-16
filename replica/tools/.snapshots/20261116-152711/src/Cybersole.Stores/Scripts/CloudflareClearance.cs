using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Stores.Flows;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The bridge between the Cloudflare ladder and a running flow: detect the wall, run the ladder, and
/// put the clearance where the next request will pick it up (R140).
///
/// <para>
/// <see cref="StoreFlow.DetectAsync"/> already names the vendor from the body and the
/// <c>server</c> header, and <c>AntiBotProtocol</c> already says the Cloudflare cookie is
/// <c>cf_clearance</c>. What was missing is the middle: nobody asked the strategy for a token and
/// nobody wrote the answer back. That is the same shape of gap R133/R134 found on the payment side, and
/// it is worth naming the pattern: <b>detection and storage both existed; the call between them did
/// not</b>.
/// </para>
///
/// <para>
/// One live observation is recorded with it: <c>cf-solver.cybersole.io</c> answered
/// <b>401</b> when this session probed it, which means the host is real and reachable and simply
/// refuses unauthenticated calls. That is more than the Kasada road has — there the host is unknown —
/// and it is why the service call here is injected rather than absent.
/// </para>
/// </summary>
public static class CloudflareClearance
{
    /// <summary>The status the service host answered when probed — real, and it wanted credentials.</summary>
    public const int ServiceStatusObserved = 401;

    /// <summary>What the observed 401 means, in words a reader can act on.</summary>
    public const string ServiceStatusMeaning =
        "cf-solver.cybersole.io answers 401 to an unauthenticated call: the host is real and reachable, " +
        "the protocol needs credentials this workspace does not have";

    /// <summary>The session keys this helper reads and writes.</summary>
    public const string VendorVar = "antibot";
    public const string SolverStatusVar = "cloudflare.solverStatus";
    public const string ClearanceVar = "cloudflare.clearance";

    /// <summary>True when the detected vendor is Cloudflare.</summary>
    public static bool IsCloudflare(FlowSession session) =>
        session.Vars.TryGetValue(VendorVar, out var vendor)
        && string.Equals(vendor, "cloudflare", System.StringComparison.OrdinalIgnoreCase);

    /// <summary>
    /// Run the ladder when the wall is Cloudflare's, then store the clearance both as a session var and
    /// as the cookie the next request needs.
    ///
    /// <para>
    /// A wall that is not Cloudflare's is not this helper's business: it returns success and stores
    /// nothing, so a Kasada or DataDome store is untouched.
    /// </para>
    /// </summary>
    public static async Task<StepOutcome> ApplyAsync(FlowContext c, CloudflareStrategyRunner runner,
        string pageUrl, CancellationToken ct = default)
    {
        if (!IsCloudflare(c.Session)) return StepOutcome.Success();

        var (token, status) = await runner.GetAsync(pageUrl, ct).ConfigureAwait(false);

        c.Session.Vars[SolverStatusVar] = status;

        if (string.IsNullOrEmpty(token))
        {
            // The refusal sentence is the image's own wording, so it goes out as a status line rather
            // than as an error: the flow continues and the next request retries without clearance.
            c.Emit($"{status}", "antibot");
            return StepOutcome.Success();
        }

        c.Session.Vars[ClearanceVar] = token;
        c.Session.Cookies[CloudflareStrategy.ClearanceCookie] = token;
        c.Emit($"Cloudflare clearance acquired ({status})", "antibot");

        return StepOutcome.Success();
    }

    /// <summary>The clearance this session holds, or null.</summary>
    public static string? Clearance(FlowSession session) =>
        session.Vars.TryGetValue(ClearanceVar, out var value) && value.Length > 0 ? value : null;

    /// <summary>The ladder's status as the session recorded it, or null.</summary>
    public static string? SolverStatus(FlowSession session) =>
        session.Vars.TryGetValue(SolverStatusVar, out var value) ? value : null;

    /// <summary>Every key this helper writes.</summary>
    public static IReadOnlyList<string> Keys = new[] { SolverStatusVar, ClearanceVar };
}
