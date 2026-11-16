using Cybersole.Core.Models;
using Cybersole.Http;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Mutable state carried across the steps of one web task — the equivalent of the
/// browser session the original keeps while walking a store flow.
/// </summary>
public sealed class FlowSession
{
    public Dictionary<string, string> Cookies { get; } = new(StringComparer.OrdinalIgnoreCase);
    public Dictionary<string, string> Headers { get; } = new(StringComparer.OrdinalIgnoreCase);
    public Dictionary<string, string> Vars { get; } = new(StringComparer.OrdinalIgnoreCase);

    public string? UserAgent { get; set; }
    public string? CsrfToken { get; set; }
    public string? SessionId { get; set; }
    public string? CartId { get; set; }
    public string? CheckoutToken { get; set; }
    public string? CheckoutUrl { get; set; }
    public string? PaymentToken { get; set; }
    public string? PaymentMethodId { get; set; }
    public string? OrderId { get; set; }
    public string? OrderNumber { get; set; }
    public string? ThreeDsUrl { get; set; }
    public string? TrackingUrl { get; set; }

    /// <summary>Variant actually selected for the cart.</summary>
    public string? VariantId { get; set; }
    public string? VariantTitle { get; set; }
    public int Quantity { get; set; } = 1;

    /// <summary>Anti-bot tokens accumulated during the flow (kpsdk, turnstile, datadome…).</summary>
    public Dictionary<string, string> AntiBotTokens { get; } = new(StringComparer.OrdinalIgnoreCase);

    public void AbsorbCookies(IReadOnlyDictionary<string, string>? cookies)
    {
        if (cookies is null) return;
        foreach (var kv in cookies) Cookies[kv.Key] = kv.Value;
    }

    public string CookieHeader() => string.Join("; ", Cookies.Select(kv => $"{kv.Key}={kv.Value}"));

    public void Clear() => Cookies.Clear();
}

/// <summary>Everything a flow step needs to run.</summary>
public sealed class FlowContext
{
    public required NetClient Http { get; init; }
    public required string Url { get; init; }
    public Product? Product { get; init; }
    public Profile? ProfileData { get; init; }
    public Account? Account { get; init; }
    public Card? Card { get; init; }
    public Address? Shipping { get; init; }
    public Address? Billing { get; init; }
    public Proxy? Proxy { get; init; }
    public TlsProfile BrowserProfile { get; init; } = TlsProfile.Chrome;
    public int TimeoutSeconds { get; init; } = 20;
    public bool MonitorOnly { get; init; }

    public FlowSession Session { get; } = new();
    public List<TaskStep> Steps { get; } = new();
    public List<MonitorEvent> Events { get; } = new();

    public Action<string>? Log { get; init; }
    public Action<TaskStep>? OnStep { get; init; }

    public FlowContext CloneFor(string url) => new()
    {
        Http = Http,
        Url = url,
        Product = Product,
        ProfileData = ProfileData,
        Account = Account,
        Card = Card,
        Shipping = Shipping,
        Billing = Billing,
        Proxy = Proxy,
        BrowserProfile = BrowserProfile,
        TimeoutSeconds = TimeoutSeconds,
        MonitorOnly = MonitorOnly,
        Log = Log,
        OnStep = OnStep,
    };

    public RequestOptions Options(string? tag = null)
    {
        var o = new RequestOptions
        {
            Proxy = Proxy?.Uri,
            Profile = BrowserProfile,
            Timeout = TimeSpan.FromSeconds(Math.Max(3, TimeoutSeconds)),
            Tag = tag,
        };
        foreach (var kv in Session.Headers) o.Headers[kv.Key] = kv.Value;
        foreach (var kv in Session.Cookies) o.Cookies[kv.Key] = kv.Value;
        foreach (var kv in Session.AntiBotTokens) o.Headers[kv.Key] = kv.Value;

        var userAgent = Session.UserAgent;
        if (HasKasadaToken && !string.IsNullOrEmpty(KasadaUserAgent))
        {
            // A Kasada token encodes the identity it was minted under. Presenting a different
            // UA is not "slightly off" — the store rejects the token outright, so pin it.
            userAgent = KasadaUserAgent;
            if (!string.IsNullOrEmpty(Session.UserAgent) && Session.UserAgent != KasadaUserAgent)
                Session.Vars["kasada.uaCorrection"] = Session.UserAgent!;
            Session.UserAgent = KasadaUserAgent;
        }

        if (!string.IsNullOrEmpty(userAgent)) o.Headers["User-Agent"] = userAgent!;
        return o;
    }

    /// <summary>True once a Kasada client token is present on the session.</summary>
    public bool HasKasadaToken => Session.AntiBotTokens.ContainsKey("x-kpsdk-ct");

    /// <summary>The user agent the Kasada token was minted under, if it was recorded.</summary>
    public string? KasadaUserAgent =>
        Session.Vars.TryGetValue("kasada.ua", out var ua) && !string.IsNullOrWhiteSpace(ua)
            ? ua
            : null;

    public void Emit(string message, string? type = null)
    {
        Log?.Invoke(message);
        Events.Add(new MonitorEvent { Name = message, Type = type, Store = Product?.Name });
    }

    public TaskStep Step(string name)
    {
        var s = new TaskStep { Name = name }.Begin();
        Steps.Add(s);
        OnStep?.Invoke(s);
        return s;
    }

    public void Finish(TaskStep step, bool ok, string? error = null)
    {
        step.End(ok, error);
        OnStep?.Invoke(step);
        if (!ok && error is not null) Emit($"{step.Name}: {error}", "error");
    }
}

/// <summary>Outcome of one flow step.</summary>
public readonly struct StepOutcome
{
    public bool Ok { get; init; }
    public string? Error { get; init; }
    public bool Retryable { get; init; }
    public bool Abort { get; init; }

    public static StepOutcome Success() => new() { Ok = true };
    public static StepOutcome Fail(string error, bool retryable = false) =>
        new() { Ok = false, Error = error, Retryable = retryable };
    public static StepOutcome Stop(string reason) =>
        new() { Ok = false, Error = reason, Abort = true };
}
