import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\CloudflareStrategy.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    public ServiceCloudflareSolver(
        System.Func<string, string, CancellationToken, Task<string?>>? call = null) => _call = call;'''

new = '''    private readonly PollingSolver? _polling;

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
    public bool IsPolling => _polling is not null;'''

if old not in t:
    raise SystemExit("service ctor anchor missing")
t = t.replace(old, new, 1)

old2 = '''    public bool IsConfigured => _call is not null;'''
new2 = '''    public bool IsConfigured => _polling is not null || _call is not null;'''
if old2 not in t:
    raise SystemExit("configured anchor missing")
t = t.replace(old2, new2, 1)

old3 = '''        if (!IsConfigured) return string.Empty;

        var token = await _call!(CloudflareStrategy.ServiceHost, pageUrl, ct).ConfigureAwait(false);'''
new3 = '''        if (!IsConfigured) return string.Empty;

        if (_polling is not null)
        {
            var polled = await _polling.GetAsync(ct).ConfigureAwait(false);
            return polled.Usable ? polled.Token : string.Empty;
        }

        var token = await _call!(CloudflareStrategy.ServiceHost, pageUrl, ct).ConfigureAwait(false);'''

if old3 not in t:
    raise SystemExit("call anchor missing")
t = t.replace(old3, new3, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("ServiceCloudflareSolver can poll")
