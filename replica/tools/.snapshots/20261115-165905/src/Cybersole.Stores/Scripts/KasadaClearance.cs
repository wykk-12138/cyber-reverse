using System.Threading;
using System.Threading.Tasks;
using Cybersole.Stores.Flows;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The Kasada half of R140's fix: detect → run the four-road strategy → store the token (R141).
///
/// <para>
/// <c>AntiBotProtocol</c> says the Kasada cookie is <c>kpsdk</c>, and R136/R137 built the strategy that
/// produces the token. Nothing joined them, which is the same gap Cloudflare had one round earlier —
/// so the shape of the fix is deliberately identical, down to the two places the result is written.
/// </para>
///
/// <para>
/// The token travels with its road (see <see cref="KasadaToken"/>): a caller that got a fallback token
/// should be able to see that it did, and the status var keeps it.
/// </para>
/// </summary>
public static class KasadaClearance
{
    public const string TokenVar = "kasada.token";
    public const string ModeVar = "kasada.mode";
    public const string StatusVar = "kasada.status";

    /// <summary>True when the detected vendor is Kasada.</summary>
    public static bool IsKasada(FlowSession session) =>
        session.Vars.TryGetValue(CloudflareClearance.VendorVar, out var vendor)
        && string.Equals(vendor, "kasada", System.StringComparison.OrdinalIgnoreCase);

    /// <summary>
    /// Run the strategy when the wall is Kasada's, then store the token as a var, as the cookie the next
    /// request needs, and record which road produced it.
    ///
    /// <para>
    /// A give-up is not a thrown exception: the status string carries every road that was tried, which
    /// is exactly what the image's <c>Failed Kasada (Retry limit reached)</c> plus its rotation messages
    /// are for.
    /// </para>
    /// </summary>
    public static async Task<StepOutcome> ApplyAsync(FlowContext c, KasadaStrategyRunner runner,
        string pageUrl, CancellationToken ct = default)
    {
        if (!IsKasada(c.Session)) return StepOutcome.Success();

        var token = await runner.GetAsync(pageUrl, ct).ConfigureAwait(false);

        c.Session.Vars[StatusVar] = token.Status;
        c.Session.Vars[ModeVar] = token.Mode.ToString();

        if (!token.Usable)
        {
            c.Emit(token.Status, "antibot");
            return StepOutcome.Success();
        }

        c.Session.Vars[TokenVar] = token.Token;

        // the image's cookie family for Kasada is kpsdk; the token is what the header carries, so the
        // cookie is written only when a cookie name is actually known
        var cookies = AntiBotProtocol.CookiesFor("Kasada");
        if (cookies is { Count: > 0 })
            c.Session.Cookies[cookies[0]] = token.Token;

        c.Emit($"Kasada token acquired via {token.Mode}", "antibot");
        return StepOutcome.Success();
    }

    /// <summary>The token this session holds, or null.</summary>
    public static string? Token(FlowSession session) =>
        session.Vars.TryGetValue(TokenVar, out var value) && value.Length > 0 ? value : null;

    /// <summary>Which road produced the token, or null.</summary>
    public static KasadaStrategy.Mode? Mode(FlowSession session) =>
        session.Vars.TryGetValue(ModeVar, out var raw)
        && System.Enum.TryParse<KasadaStrategy.Mode>(raw, out var mode)
            ? mode
            : null;

    /// <summary>The strategy's status, or null.</summary>
    public static string? Status(FlowSession session) =>
        session.Vars.TryGetValue(StatusVar, out var value) ? value : null;
}
