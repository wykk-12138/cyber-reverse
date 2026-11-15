using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// Cloudflare's strategy, which the image spells out as the same shape as Kasada's (R139).
///
/// <para>
/// The sentence that settles it is <c>Cloudflare solver refused the token, solving in-bot</c> — a
/// service was asked, it said no, and the bot solved the wall itself. That is one step of the same
/// ladder <see cref="KasadaStrategy"/> describes: ask the service, and when the service will not help,
/// do it locally.
/// </para>
///
/// <para>
/// The service has an address, unlike Kasada's: <c>cf-solver.cybersole.io</c>, recorded whole in
/// <see cref="CybersoleHosts"/>. The registry the Settings page renders —
/// <c>CloudflareSolvers</c>, <c>CloudflareSolverId</c>, <c>CloudflareSolver.Default</c>,
/// <c>CapSolver</c>, <c>CloseSolver</c>, <c>EmptySolver.html</c> — is the page's shape, which is why a
/// solver has an id and a default.
/// </para>
/// </summary>
public static class CloudflareStrategy
{
    /// <summary>The two ways a <c>cf_clearance</c> can arrive.</summary>
    public enum Mode
    {
        /// <summary>Ask <c>cf-solver.cybersole.io</c>.</summary>
        Service,
        /// <summary>Solve it in the browser that already has the page open.</summary>
        InBot,
    }

    /// <summary>The service host, from the fifteen.</summary>
    public const string ServiceHost = "cf-solver.cybersole.io";

    /// <summary>What the service says when it will not help — verbatim, because it is shown.</summary>
    public const string RefusedMessage = "Cloudflare solver refused the token, solving in-bot";

    /// <summary>The cookie a successful solve produces.</summary>
    public const string ClearanceCookie = "cf_clearance";

    /// <summary>The registry names the Settings page needs.</summary>
    public static readonly IReadOnlyList<string> RegistryNames = new[]
    {
        "CloudflareSolvers", "CloudflareSolverId", "CloudflareSolver.Default",
        "CapSolver", "CloseSolver", "EmptySolver.html",
    };

    /// <summary>True when the mode asks someone else.</summary>
    public static bool IsService(Mode mode) => mode == Mode.Service;

    /// <summary>The mode a status line belongs to, or null.</summary>
    public static Mode? ModeFor(string? status)
    {
        if (string.IsNullOrEmpty(status)) return null;
        if (status.Contains("refused the token", System.StringComparison.Ordinal)) return Mode.Service;
        if (status.Contains("solving in-bot", System.StringComparison.Ordinal)) return Mode.InBot;
        return null;
    }
}

/// <summary>One way of producing a <c>cf_clearance</c>.</summary>
public interface ICloudflareSolver
{
    CloudflareStrategy.Mode Mode { get; }

    /// <summary>The clearance token, or an empty string when this road produced nothing.</summary>
    Task<string> GetClearanceAsync(string pageUrl, CancellationToken ct = default);
}

/// <summary>
/// Ask the service. The call is injected because the service's protocol is not in the image; what is in
/// the image is its host, its name in the registry, and the sentence it uses when it refuses.
/// </summary>
public sealed class ServiceCloudflareSolver : ICloudflareSolver
{
    private readonly System.Func<string, string, CancellationToken, Task<string?>>? _call;

    private readonly PollingSolver? _polling;

    public ServiceCloudflareSolver(
        System.Func<string, string, CancellationToken, Task<string?>>? call = null,
        PollingSolver? polling = null)
    {
        _call = call;
        _polling = polling;
    }

    /// <summary>
    /// A service road that answers later (R145) — the Cloudflare half of the same idea
    /// <c>ApiKasadaSolver.Polling</c> carries.
    /// </summary>
    public static ServiceCloudflareSolver Polling(
        System.Func<CancellationToken, Task<string?>> probe,
        TimeSpan? interval = null, int attempts = 20) =>
        new(polling: new PollingSolver(probe, KasadaStrategy.Mode.Api, interval, attempts));

    /// <summary>True when this road polls rather than calls once.</summary>
    public bool IsPolling => _polling is not null;

    public CloudflareStrategy.Mode Mode => CloudflareStrategy.Mode.Service;

    /// <summary>True when a transport was supplied.</summary>
    public bool IsConfigured => _polling is not null || _call is not null;

    public async Task<string> GetClearanceAsync(string pageUrl, CancellationToken ct = default)
    {
        if (!IsConfigured) return string.Empty;

        if (_polling is not null)
        {
            var polled = await _polling.GetAsync(ct).ConfigureAwait(false);
            return polled.Usable ? polled.Token : string.Empty;
        }

        var token = await _call!(CloudflareStrategy.ServiceHost, pageUrl, ct).ConfigureAwait(false);
        return token ?? string.Empty;
    }
}

/// <summary>
/// Solve it in the browser. The work itself belongs to the bridge; this class only answers the
/// strategy question — it is the <c>in-bot</c> half, and its name is the second half of the image's
/// sentence.
/// </summary>
public sealed class InBotCloudflareSolver : ICloudflareSolver
{
    private readonly System.Func<string, CancellationToken, Task<string?>>? _solve;

    public InBotCloudflareSolver(System.Func<string, CancellationToken, Task<string?>>? solve = null) =>
        _solve = solve;

    public CloudflareStrategy.Mode Mode => CloudflareStrategy.Mode.InBot;

    public async Task<string> GetClearanceAsync(string pageUrl, CancellationToken ct = default)
    {
        if (_solve is null) return string.Empty;

        var token = await _solve(pageUrl, ct).ConfigureAwait(false);
        return token ?? string.Empty;
    }
}

/// <summary>
/// The ladder: service first, then in-bot. The refusal is not an error — it is the reason to fall
/// through, which is why the runner reports it as a status rather than a failure.
/// </summary>
public sealed class CloudflareStrategyRunner
{
    private readonly ICloudflareSolver _service;
    private readonly ICloudflareSolver _inBot;

    public CloudflareStrategyRunner(ICloudflareSolver service, ICloudflareSolver inBot)
    {
        _service = service;
        _inBot = inBot;
    }

    /// <summary>Service then in-bot, with the service configured by injection.</summary>
    public static CloudflareStrategyRunner Default(
        System.Func<string, string, CancellationToken, Task<string?>>? serviceCall = null,
        System.Func<string, CancellationToken, Task<string?>>? inBotSolve = null) =>
        new(new ServiceCloudflareSolver(serviceCall), new InBotCloudflareSolver(inBotSolve));

    /// <summary>The order, which is the whole content of the strategy.</summary>
    public IReadOnlyList<CloudflareStrategy.Mode> Order => new[]
    {
        CloudflareStrategy.Mode.Service, CloudflareStrategy.Mode.InBot,
    };

    /// <summary>
    /// Run the ladder. Returns the clearance and the status that produced it; when both roads are
    /// empty the status is the refusal sentence, so a caller can show exactly what the image shows.
    /// </summary>
    public async Task<(string Token, string Status)> GetAsync(string pageUrl,
        CancellationToken ct = default)
    {
        var service = await _service.GetClearanceAsync(pageUrl, ct).ConfigureAwait(false);
        if (!string.IsNullOrEmpty(service))
            return (service, "Cloudflare solver produced the token");

        var inBot = await _inBot.GetClearanceAsync(pageUrl, ct).ConfigureAwait(false);
        if (!string.IsNullOrEmpty(inBot))
            return (inBot, CloudflareStrategy.RefusedMessage);

        return (string.Empty, CloudflareStrategy.RefusedMessage);
    }
}
