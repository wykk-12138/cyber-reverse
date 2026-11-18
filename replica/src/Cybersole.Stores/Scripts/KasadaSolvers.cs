using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// A token, plus which of the four roads it came from.
///
/// <para>
/// The mode travels with the token because the caller has to know: a fallback token is usable but it is
/// not the same thing as a solved one, and the image says so in its own status strings
/// (<c>Kasada-Fallback</c>, <c>Kasada-Mobile-Fallback</c>).
/// </para>
/// </summary>
public sealed record KasadaToken(string Token, KasadaStrategy.Mode Mode, string Status)
{
    /// <summary>True when there is something to send on the next request.</summary>
    public bool Usable => !string.IsNullOrEmpty(Token);

    /// <summary>A failure that carries the status a UI should show.</summary>
    public static KasadaToken Failed(string status, KasadaStrategy.Mode mode) =>
        new(string.Empty, mode, status);
}

/// <summary>
/// The interface the image declares, and the reason its four modes are interchangeable.
///
/// <para>
/// Each implementation answers for exactly one mode. A solver that cannot produce a token returns
/// <see cref="KasadaToken.Failed"/> with the status the image uses for that mode, so the runner never
/// has to guess why a road was empty.
/// </para>
/// </summary>
public interface IKasadaSolver
{
    /// <summary>Which road this implementation is.</summary>
    KasadaStrategy.Mode Mode { get; }

    /// <summary>Try to produce a token for <paramref name="pageUrl"/>.</summary>
    Task<KasadaToken> GetAsync(string pageUrl, CancellationToken ct = default);
}

/// <summary>
/// The <c>Local</c> road: run the page in a browser and read the token it puts on the wire.
/// Wraps the bridge that already exists — this class adds nothing but the interface.
/// </summary>
public sealed class LocalKasadaSolver : IKasadaSolver
{
    private readonly ChromiumKasadaSolver? _solver;

    /* No browser is created implicitly. The constructor used to do `solver ?? new ChromiumKasadaSolver()`,
       which meant a caller that supplied null -- precisely the "no browser installed" case -- still got a
       road that launched one, so a default runner spun up Chromium and took tens of seconds to report a
       failure it could have reported immediately. */
    public LocalKasadaSolver(ChromiumKasadaSolver? solver = null) => _solver = solver;

    public KasadaStrategy.Mode Mode => KasadaStrategy.Mode.Local;

    public async Task<KasadaToken> GetAsync(string pageUrl, CancellationToken ct = default)
    {
        if (_solver is null)
            return KasadaToken.Failed("Failed solving Kasada", Mode);

        var result = await _solver.SolveAsync(pageUrl, ct: ct).ConfigureAwait(false);

        if (result is null || string.IsNullOrEmpty(result.Ct))
            return KasadaToken.Failed("Failed solving Kasada", Mode);

        return new KasadaToken(result.Ct!, Mode, "Solved Kasada");
    }
}

/// <summary>
/// The <c>Api</c> road: ask a service for a token.
///
/// <para>
/// <b>The endpoint is not in the image.</b> The status strings prove a service exists
/// (<c>Kasada API down (Contact staff)</c> is not a message about a local failure), but they do not
/// name its address. So this solver takes the base URL by injection and, when none is configured,
/// reports the image's own operator message rather than inventing a host — the same rule that
/// <c>endpoint-provenance.py</c> enforces for every other endpoint in this workspace.
/// </para>
/// </summary>
public sealed class ApiKasadaSolver : IKasadaSolver
{
    private readonly string? _endpoint;
    private readonly System.Func<string, string, CancellationToken, Task<string?>>? _call;

    private readonly PollingSolver? _polling;

    public ApiKasadaSolver(string? endpoint = null,
        System.Func<string, string, CancellationToken, Task<string?>>? call = null,
        PollingSolver? polling = null)
    {
        _endpoint = endpoint;
        _call = call;
        _polling = polling;
    }

    /// <summary>
    /// An API road that answers later: the probe is asked again on an interval until it produces a
    /// token or the budget runs out (R145).
    ///
    /// <para>
    /// This is the shape <c>PollCaptchaAsync</c> implies. A one-shot call cannot tell "not ready" from
    /// "refused", and a service that hands out tokens asynchronously answers "not ready" for the first
    /// few looks by design.
    /// </para>
    /// </summary>
    public static ApiKasadaSolver Polling(System.Func<CancellationToken, Task<string?>> probe,
        TimeSpan? interval = null, int attempts = 20) =>
        new(endpoint: "polling", polling: new PollingSolver(probe, KasadaStrategy.Mode.Api,
            interval, attempts));

    /// <summary>True when this road polls rather than calls once.</summary>
    public bool IsPolling => _polling is not null;

    public KasadaStrategy.Mode Mode => KasadaStrategy.Mode.Api;

    /// <summary>True when an address was supplied — the only case where a request is attempted.</summary>
    public bool IsConfigured => _polling is not null
        || (!string.IsNullOrEmpty(_endpoint) && _call is not null);

    public async Task<KasadaToken> GetAsync(string pageUrl, CancellationToken ct = default)
    {
        if (!IsConfigured)
            return KasadaToken.Failed("Kasada API down (Contact staff)", Mode);

        if (_polling is not null) return await _polling.GetAsync(ct).ConfigureAwait(false);

        var token = await _call!(_endpoint!, pageUrl, ct).ConfigureAwait(false);

        return string.IsNullOrEmpty(token)
            ? KasadaToken.Failed("Failed getting Kasada", Mode)
            : new KasadaToken(token!, Mode, "Getting Kasada (1)");
    }
}

/// <summary>
/// One of the two named fallbacks. It has no producer of its own — a fallback token comes from
/// somewhere the image does not describe — so it reports its own name and nothing else.
/// </summary>
public sealed class NamedFallbackSolver : IKasadaSolver
{
    private readonly System.Func<string, CancellationToken, Task<string?>>? _produce;

    public NamedFallbackSolver(KasadaStrategy.Mode mode = KasadaStrategy.Mode.Fallback,
        System.Func<string, CancellationToken, Task<string?>>? produce = null)
    {
        if (mode is not (KasadaStrategy.Mode.Fallback or KasadaStrategy.Mode.MobileFallback))
            throw new System.ArgumentOutOfRangeException(nameof(mode), "only the two fallback modes");

        Mode = mode;
        _produce = produce;
    }

    public KasadaStrategy.Mode Mode { get; }

    /// <summary>The status this road reports, taken from the image's own spelling.</summary>
    public string StatusName => Mode == KasadaStrategy.Mode.Fallback
        ? KasadaStrategy.Fallback
        : KasadaStrategy.MobileFallback;

    public async Task<KasadaToken> GetAsync(string pageUrl, CancellationToken ct = default)
    {
        if (_produce is null) return KasadaToken.Failed(StatusName, Mode);

        var token = await _produce(pageUrl, ct).ConfigureAwait(false);
        return string.IsNullOrEmpty(token)
            ? KasadaToken.Failed(StatusName, Mode)
            : new KasadaToken(token!, Mode, StatusName);
    }
}

/// <summary>
/// The strategy: try the roads in the order the image's strings imply, stop at the first token, and
/// report every road that was tried.
///
/// <para>
/// The order is <c>Api</c> → <c>Local</c> → <c>Fallback</c> → <c>MobileFallback</c>. "Getting" comes
/// before "solving" because getting is cheap and the image numbers its attempts (<c>Getting Kasada
/// (1)</c>, <c>(2)</c>), which only makes sense if it is tried first and retried; the fallbacks come
/// last because a fallback token is the last thing anyone wants.
/// </para>
///
/// <para>
/// When every road is empty the runner returns the image's own give-up string,
/// <c>Failed Kasada (Retry limit reached)</c>, with the list of statuses that led there.
/// </para>
/// </summary>
/// <summary>
/// WHY THIS EXISTS: the strategy runner had three roads (an external service, a browser, and two named
/// fallbacks) and none of them ran the page's own script. For every store except Nike that left the whole
/// Kasada step unable to produce a token, and the flow carried on without one. This road runs the payload
/// locally with the interrogation path the Nike flow already uses: configure the sensor with the page
/// origin, let it issue GET /mfc then POST /r through the caller's HTTP stack, and read x-kpsdk-ct off the
/// reply.
/// </summary>
public sealed class ScriptKasadaSolver : IKasadaSolver
{
    private readonly Cybersole.Http.NetClient _http;

    public ScriptKasadaSolver(Cybersole.Http.NetClient http) => _http = http;

    public KasadaStrategy.Mode Mode => KasadaStrategy.Mode.Local;

    public async Task<KasadaToken> GetAsync(string pageUrl, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(pageUrl))
            return KasadaToken.Failed(KasadaStrategy.Verb(Mode) + " kasada", Mode);

        var origin = KasadaSolver.OriginOf(pageUrl);
        if (origin is null) return KasadaToken.Failed(KasadaStrategy.Verb(Mode) + " kasada", Mode);

        // Bounded: this is on the checkout path, so a slow interrogation endpoint must not hold the flow.
        var options = new Cybersole.Http.RequestOptions
        {
            Timeout = TimeSpan.FromSeconds(15),
            Retries = 0,
        };

        using var solver = new KasadaSolver(new BrowserShim { Href = pageUrl });
        string? script;
        try
        {
            (script, _) = await solver.FetchScriptAsync(_http, pageUrl, options, ct).ConfigureAwait(false);
        }
        catch (Exception ex) when (ex is not OperationCanceledException and not OutOfMemoryException)
        {
            // A road reports failure; it does not abort the runner. An escaping exception here would stop
            // the remaining roads from being tried, which is the opposite of what a fallback chain is for.
            return KasadaToken.Failed(KasadaStrategy.Verb(Mode) + " kasada: " + ex.Message, Mode);
        }

        if (script is null) return KasadaToken.Failed(KasadaStrategy.Verb(Mode) + " kasada", Mode);

        solver.ResourceAddress = origin;
        solver.Transport = KasadaSolver.NetTransport(_http, options);

        // The transport resolves asynchronously beneath a synchronous script call, so keep that wait off
        // this thread instead of blocking on it.
        var result = await Task.Run(() => solver.Solve(script), ct).ConfigureAwait(false);

        return result.Ok && !string.IsNullOrEmpty(result.Ct)
            ? new KasadaToken(result.Ct!, Mode, KasadaStrategy.Verb(Mode) + " kasada")
            : KasadaToken.Failed(KasadaStrategy.Verb(Mode) + " kasada", Mode);
    }
}

public sealed class KasadaStrategyRunner
{
    public const string GaveUpStatus = "Failed Kasada (Retry limit reached)";

    private readonly IReadOnlyList<IKasadaSolver> _solvers;

    public KasadaStrategyRunner(IEnumerable<IKasadaSolver> solvers) =>
        _solvers = new List<IKasadaSolver>(solvers);

    /// <summary>The default order, with only the roads that were supplied.</summary>
    public static KasadaStrategyRunner Default(string? apiEndpoint = null,
        ChromiumKasadaSolver? local = null,
        System.Func<string, string, CancellationToken, Task<string?>>? apiCall = null,
        IKasadaSolver? script = null)
    {
        // Exactly four roads, matching the four modes the image declares. Local is always present so the
        // runner can report why it could not solve, even with nothing supplied -- but a script road wins
        // over a browser one when both are available, because it needs no Chromium install to work.
        var localRoad = script ?? new LocalKasadaSolver(local);
        return new KasadaStrategyRunner(new IKasadaSolver[]
        {
            new ApiKasadaSolver(apiEndpoint, apiCall),
            localRoad,
            new NamedFallbackSolver(KasadaStrategy.Mode.Fallback),
            new NamedFallbackSolver(KasadaStrategy.Mode.MobileFallback),
        });
    }

    /// <summary>Every road, in the order they are tried.</summary>
    public IReadOnlyList<KasadaStrategy.Mode> Order =>
        _solvers.Select(s => s.Mode).ToList().AsReadOnly();

    /// <summary>
    /// Try each road once. Returns the first usable token, or a give-up token carrying every status.
    /// </summary>
    public async Task<KasadaToken> GetAsync(string pageUrl, CancellationToken ct = default)
    {
        var statuses = new List<string>();

        foreach (var solver in _solvers)
        {
            var token = await solver.GetAsync(pageUrl, ct).ConfigureAwait(false);
            statuses.Add(token.Status);

            if (token.Usable) return token;
        }

        var gaveUp = KasadaToken.Failed(GaveUpStatus, KasadaStrategy.Mode.Local);
        return new KasadaToken(gaveUp.Token, gaveUp.Mode, string.Join(" | ", statuses.Append(GaveUpStatus)));
    }
}
