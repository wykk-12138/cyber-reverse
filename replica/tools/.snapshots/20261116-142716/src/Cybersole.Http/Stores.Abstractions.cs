using Cybersole.Core.Models;

namespace Cybersole.Http.Stores;

/// <summary>Result of a single monitor poll.</summary>
public enum MonitorStatus
{
    Unavailable = 0,
    Available = 1,
    SoldOut = 2,
    Captcha = 3,
    Blocked = 4,
    Error = 5,
}

public sealed class MonitorResult
{
    public MonitorStatus Status { get; init; }
    public bool InStock => Status == MonitorStatus.Available;
    public string? ProductName { get; init; }
    public string? Image { get; init; }
    public string? Price { get; init; }
    public string? VariantId { get; init; }
    public string? VariantTitle { get; init; }
    public List<string> Sizes { get; init; } = new();
    public string? Raw { get; init; }
    public string? Error { get; init; }

    public static MonitorResult Fail(string error) => new() { Status = MonitorStatus.Error, Error = error };
    public static MonitorResult SoldOut() => new() { Status = MonitorStatus.SoldOut };
}

public sealed class MonitorContext
{
    public required NetClient Http { get; init; }
    public required string Url { get; init; }
    public Product? Product { get; init; }
    public Proxy? Proxy { get; init; }
    public TlsProfile Profile { get; init; } = TlsProfile.Chrome;
    public int TimeoutSeconds { get; init; } = 10;

    /// <summary>Cloudflare provider picked for this group (null = the global default).</summary>
    public string? CloudflareProviderId { get; init; }

    /// <summary>Captcha provider picked for this group (null = the global priority list).</summary>
    public string? CaptchaProviderId { get; init; }

    /// <summary>The task group this run belongs to, when one was picked.</summary>
    public string? GroupId { get; init; }
}

public sealed class CheckoutContext
{
    public required NetClient Http { get; init; }
    public required string Url { get; init; }
    public required string VariantId { get; init; }
    public required string Size { get; init; }
    public required Profile ProfileData { get; init; }
    public Account? Account { get; init; }
    public Proxy? Proxy { get; init; }
    public TlsProfile BrowserProfile { get; init; } = TlsProfile.Chrome;
    public int TimeoutSeconds { get; init; } = 20;
    public Dictionary<string, string> Extra { get; init; } = new(StringComparer.OrdinalIgnoreCase);
}

public sealed class CheckoutOutcome
{
    public bool Success { get; init; }
    public string? OrderNumber { get; init; }
    public string? Error { get; init; }
    public string? Price { get; init; }
    public CheckoutResult Result { get; init; } = CheckoutResult.Unknown;
    public string? TrackingUrl { get; init; }
    public Dictionary<string, string> Details { get; init; } = new();

    /// <summary>Billing/identity fields actually submitted (from CheckoutFormBuilder).</summary>
    public Dictionary<string, string> SubmittedFields { get; init; } = new();
}

/// <summary>Captcha challenge raised by a store module.</summary>
public sealed class CaptchaChallenge
{
    public required string SiteKey { get; init; }
    public required string PageUrl { get; init; }
    public string Kind { get; init; } = "turnstile"; // turnstile | recaptcha | hcaptcha | geetest
    public string? Action { get; init; }
    public string? Proxy { get; init; }
    public string? UserAgent { get; init; }
}

/// <summary>
/// A store integration (Shopify / Nike / Footsites …).
/// Implementing types live in Cybersole.Stores.Modules.
/// </summary>
public interface IStoreModule
{
    /// <summary>Stable id, e.g. "shopify".</summary>
    string Id { get; }
    string Name { get; }
    /// <summary>Domains this module claims (used by CustomBrowser routing).</summary>
    IReadOnlyList<string> Domains { get; }

    bool CanHandle(Uri url);

    Task<MonitorResult> MonitorAsync(MonitorContext context, CancellationToken ct);

    Task<CheckoutOutcome> CheckoutAsync(CheckoutContext context, CancellationToken ct);

    /// <summary>Optional captcha hook; return null when the store does not need one.</summary>
    CaptchaChallenge? CreateChallenge(string pageUrl, string? siteKey = null, string kind = "turnstile");
}

/// <summary>Registry of every store module known to the app.</summary>
public sealed class StoreRegistry
{
    private readonly List<IStoreModule> _modules = new();

    public IReadOnlyList<IStoreModule> Modules => _modules;

    public void Register(IStoreModule module)
    {
        if (_modules.All(m => m.Id != module.Id))
            _modules.Add(module);
    }

    /// <summary>
    /// Longest-domain match wins, so a specific alias always beats a generic module regardless of
    /// registration order (a generic "shopify.com" must never shadow "my-shop.shopify.com").
    /// </summary>
    public IStoreModule? Resolve(Uri url)
    {
        IStoreModule? best = null;
        var bestLength = -1;

        foreach (var module in _modules)
        {
            if (!module.CanHandle(url)) continue;

            var length = module.Domains
                .Where(d => !string.IsNullOrEmpty(d) &&
                            url.Host.EndsWith(d, StringComparison.OrdinalIgnoreCase))
                .Select(d => d.Length)
                .DefaultIfEmpty(0)
                .Max();

            if (length > bestLength)
            {
                best = module;
                bestLength = length;
            }
        }

        return best;
    }

    public IStoreModule? Resolve(string id) =>
        _modules.FirstOrDefault(m => string.Equals(m.Id, id, StringComparison.OrdinalIgnoreCase));
}
