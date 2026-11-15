using System.Diagnostics;
using Cybersole.Core.Models;
using Cybersole.Core.Store;
using Cybersole.Http;

namespace Cybersole.Services;

public sealed class ProxyTestResult
{
    public required Proxy Proxy { get; init; }
    public bool Ok { get; init; }
    public int LatencyMs { get; init; }
    public string? ExitIp { get; init; }
    public string? Country { get; init; }
    public string? Error { get; init; }
}

/// <summary>Concurrent proxy validation (Cybersole.ProxyTesters.ProxyTester).</summary>
public sealed class ProxyTester
{
    private readonly EventBus _bus;
    public const string IpEchoUrl = "https://api.ipify.org?format=json";

    /// <summary>
    /// R511: the original binds <c>Name</c> on <c>Cybersole.ProxyTesters.ProxyTester</c> — the descriptor table
    /// lists exactly one member for that type, and it is this one, <b>Getter only</b>.
    /// </summary>
    /// <remarks>
    /// <para>
    /// R488 had judged this "evidence conflict" because the lookup used the wrong namespace
    /// (<c>Cybersole.Services.ProxyTester</c>, which is what the replica calls it). The original's namespace is
    /// <c>Cybersole.ProxyTesters</c>. With the right name the conflict disappears: the member exists.
    /// </para>
    /// <para>
    /// <b>What the string says is still unknown.</b> The locale pool has four keys under this prefix
    /// (<c>ProxyTester.Custom.Button</c> / <c>.InvalidUrl</c> / <c>.Placeholder</c> / <c>.Title</c>) but no bare
    /// <c>ProxyTester</c> value, so there is no observed label to copy. The class name is used as a stand-in and
    /// this note is the reason it may be wrong.
    /// </para>
    /// </remarks>
    public string Name { get; } = nameof(ProxyTester);

    public ProxyTester(EventBus bus) => _bus = bus;

    /// <summary>
    /// Checks one proxy by fetching <paramref name="targetUrl"/> through it.
    /// </summary>
    /// <param name="targetUrl">
    /// Defaults to <see cref="IpEchoUrl"/>, which answers "does this proxy work at all".
    ///
    /// R58: the locale has <c>Proxies.More.TestAllOn</c> ("Test All On:") and
    /// <c>Proxies.More.SelectSite</c> ("Select Site"), so the original can test against a
    /// particular store rather than a neutral echo. That is a different question — a proxy can
    /// reach ipify and still be blocked by the store, which is exactly what makes it useless for
    /// a drop. Passing the store's own origin asks the question that matters.
    ///
    /// The exit IP is only read when the target is the echo service; a store's home page does not
    /// report one, and parsing it for an "ip" field would invent a value.
    /// </param>
    public async Task<ProxyTestResult> TestAsync(Proxy proxy, int timeoutSeconds = 8,
        CancellationToken ct = default, string? targetUrl = null)
    {
        var url = string.IsNullOrWhiteSpace(targetUrl) ? IpEchoUrl : targetUrl!;
        var wantsExitIp = string.Equals(url, IpEchoUrl, StringComparison.OrdinalIgnoreCase);

        var sw = Stopwatch.StartNew();
        try
        {
            using var handler = new SocketsHttpHandler
            {
                Proxy = new System.Net.WebProxy(proxy.Uri),
                UseProxy = true,
                ConnectTimeout = TimeSpan.FromSeconds(timeoutSeconds),
                AutomaticDecompression = System.Net.DecompressionMethods.All,
            };
            using var client = new HttpClient(handler) { Timeout = TimeSpan.FromSeconds(timeoutSeconds) };
            var body = await client.GetStringAsync(url, ct).ConfigureAwait(false);
            sw.Stop();

            var ip = wantsExitIp ? Newtonsoft.Json.Linq.JObject.Parse(body)["ip"]?.ToString() : null;
            proxy.Status = Status.Running;
            return new ProxyTestResult
            {
                Proxy = proxy,
                Ok = true,
                LatencyMs = (int)sw.ElapsedMilliseconds,
                ExitIp = ip,
            };
        }
        catch (Exception ex)
        {
            sw.Stop();
            proxy.Status = Status.Failed;
            return new ProxyTestResult
            {
                Proxy = proxy,
                Ok = false,
                LatencyMs = (int)sw.ElapsedMilliseconds,
                Error = ex.Message,
            };
        }
    }

    public async Task<IReadOnlyList<ProxyTestResult>> TestAllAsync(
        IEnumerable<Proxy> proxies, int concurrency = 25, IProgress<ProxyTestResult>? progress = null,
        CancellationToken ct = default, string? targetUrl = null)
    {
        var results = new System.Collections.Concurrent.ConcurrentBag<ProxyTestResult>();
        using var gate = new SemaphoreSlim(Math.Max(1, concurrency));

        var tasks = proxies.Select(async p =>
        {
            await gate.WaitAsync(ct).ConfigureAwait(false);
            try
            {
                var r = await TestAsync(p, ct: ct, targetUrl: targetUrl).ConfigureAwait(false);
                results.Add(r);
                progress?.Report(r);
                _bus.Log(r.Ok ? LogLevel.Debug : LogLevel.Warn, "Proxy",
                    $"{p.Address} -> {(r.Ok ? $"{r.LatencyMs}ms {r.ExitIp}" : r.Error)}");
            }
            finally
            {
                gate.Release();
            }
        }).ToList();

        await Task.WhenAll(tasks).ConfigureAwait(false);
        return results.ToList();
    }
}
