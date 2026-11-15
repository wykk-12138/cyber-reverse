import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\KasadaSolvers.cs"
t = io.open(p, encoding="utf-8").read()

# 1) the API solver can be a poller instead of a one-shot call
old = '''    public ApiKasadaSolver(string? endpoint = null,
        System.Func<string, string, CancellationToken, Task<string?>>? call = null)
    {
        _endpoint = endpoint;
        _call = call;
    }'''

new = '''    private readonly PollingSolver? _polling;

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
    public bool IsPolling => _polling is not null;'''

if old not in t:
    raise SystemExit("api ctor anchor missing")
t = t.replace(old, new, 1)

# 2) the call path honours it
old2 = '''    public bool IsConfigured => !string.IsNullOrEmpty(_endpoint) && _call is not null;'''
new2 = '''    public bool IsConfigured => _polling is not null
        || (!string.IsNullOrEmpty(_endpoint) && _call is not null);'''

if old2 not in t:
    raise SystemExit("configured anchor missing")
t = t.replace(old2, new2, 1)

old3 = '''        if (!IsConfigured)
            return KasadaToken.Failed("Kasada API down (Contact staff)", Mode);

        var token = await _call!(_endpoint!, pageUrl, ct).ConfigureAwait(false);'''
new3 = '''        if (!IsConfigured)
            return KasadaToken.Failed("Kasada API down (Contact staff)", Mode);

        if (_polling is not null) return await _polling.GetAsync(ct).ConfigureAwait(false);

        var token = await _call!(_endpoint!, pageUrl, ct).ConfigureAwait(false);'''

if old3 not in t:
    raise SystemExit("call anchor missing")
t = t.replace(old3, new3, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("ApiKasadaSolver can poll")
