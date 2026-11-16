using System;
using System.Threading;
using System.Threading.Tasks;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The polling road, which R143 found in the image as <c>PollCaptchaAsync</c> (R144).
///
/// <para>
/// A local browser solve finishes when it finishes: the token is there or the page failed. A service
/// does not work that way — it accepts a job and answers later, which is why the image has a method whose
/// name is <b>Poll</b> rather than <b>Solve</b>. The replica's ladders all awaited inline, so a service
/// that answered on the second look was indistinguishable from one that refused.
/// </para>
///
/// <para>
/// This decorator is deliberately tiny: a probe, an interval, a deadline. It does not know which vendor
/// it belongs to, because the shape is the same for all of them — the strategy supplies the probe and
/// keeps ownership of the modes.
/// </para>
///
/// <para>
/// <b>Bounded, and honest when it gives up.</b> The status it returns says how many looks were taken and
/// how long it waited, so a failure explains itself in the same spirit as the rest of this workspace.
/// </para>
/// </summary>
public sealed class PollingSolver
{
    private readonly Func<CancellationToken, Task<string?>> _probe;
    private readonly KasadaStrategy.Mode _mode;
    private readonly TimeSpan _interval;
    private readonly int _attempts;

    public PollingSolver(Func<CancellationToken, Task<string?>> probe,
        KasadaStrategy.Mode mode = KasadaStrategy.Mode.Api,
        TimeSpan? interval = null, int attempts = 20)
    {
        _probe = probe;
        _mode = mode;
        _interval = interval ?? TimeSpan.FromSeconds(1);
        _attempts = Math.Max(1, attempts);
    }

    /// <summary>How many times the probe is asked before the road gives up.</summary>
    public int Attempts => _attempts;

    /// <summary>How long the road waits between looks.</summary>
    public TimeSpan Interval => _interval;

    /// <summary>
    /// Poll until a token appears or the attempts run out.
    /// </summary>
    public async Task<KasadaToken> GetAsync(CancellationToken ct = default)
    {
        for (var attempt = 1; attempt <= _attempts; attempt++)
        {
            ct.ThrowIfCancellationRequested();

            var token = await _probe(ct).ConfigureAwait(false);
            if (!string.IsNullOrEmpty(token))
                return new KasadaToken(token!, _mode, $"Polled {attempt} time(s)");

            if (attempt < _attempts) await Task.Delay(_interval, ct).ConfigureAwait(false);
        }

        return KasadaToken.Failed(
            $"Polled {_attempts} time(s) and gave up after {_attempts * _interval.TotalSeconds:0.###}s",
            _mode);
    }

    /// <summary>The status a poll that never saw a token reports, for a caller that only needs the shape.</summary>
    public string GiveUpStatus => $"Polled {_attempts} time(s) and gave up after " +
                                  $"{_attempts * _interval.TotalSeconds:0.###}s";
}
