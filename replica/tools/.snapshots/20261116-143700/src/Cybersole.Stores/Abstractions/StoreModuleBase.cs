using System.Text.RegularExpressions;
using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Http.Stores;

namespace Cybersole.Stores.Abstractions;

/// <summary>Shared plumbing for every store module.</summary>
public abstract class StoreModuleBase : IStoreModule
{
    public abstract string Id { get; }
    public abstract string Name { get; }
    public abstract IReadOnlyList<string> Domains { get; }

    public virtual bool CanHandle(Uri url)
        => Domains.Any(d => url.Host.EndsWith(d, StringComparison.OrdinalIgnoreCase));

    public abstract Task<MonitorResult> MonitorAsync(MonitorContext context, CancellationToken ct);

    public abstract Task<CheckoutOutcome> CheckoutAsync(CheckoutContext context, CancellationToken ct);

    public virtual CaptchaChallenge? CreateChallenge(string pageUrl, string? siteKey = null,
        string kind = "turnstile")
        => string.IsNullOrEmpty(siteKey)
            ? null
            : new CaptchaChallenge { SiteKey = siteKey, PageUrl = pageUrl, Kind = kind };

    protected static RequestOptions Options(Proxy? proxy, TlsProfile profile, int timeoutSeconds,
        string? tag = null)
        => new()
        {
            Proxy = proxy?.Uri,
            Profile = profile,
            Timeout = TimeSpan.FromSeconds(Math.Max(3, timeoutSeconds)),
            Tag = tag,
        };

    protected static string? MatchGroup(string input, string pattern, int group = 1)
    {
        var m = Regex.Match(input, pattern, RegexOptions.IgnoreCase | RegexOptions.Singleline);
        return m.Success ? m.Groups[group].Value : null;
    }
}
