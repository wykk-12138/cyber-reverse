using Cybersole.Http;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Cybersole.Services.Captcha;

/// <summary>
/// A configured captcha provider row (Cybersole.CaptchaProviders.CaptchaProvider):
/// <c>{ ApiKey, Balance, BalanceSupported, Concurrency, Count, IsFetchingBalance, Name, Priority, Type }</c>.
/// </summary>
public sealed class CaptchaProviderConfig
{
    public string Type { get; set; } = "humanpresence";
    public string Name { get; set; } = string.Empty;
    public string? ApiKey { get; set; }
    public int Concurrency { get; set; } = 10;
    public int Priority { get; set; }
    public bool Enabled { get; set; } = true;
    public decimal? Balance { get; set; }
    public bool BalanceSupported { get; set; }
    public int Count { get; set; }
    public bool IsFetchingBalance { get; set; }
}

/// <summary>One provider implementation. Drivers are stateless; config is passed in.</summary>
public interface ICaptchaDriver
{
    string Type { get; }
    string Name { get; }
    bool BalanceSupported { get; }

    /// <summary>Captcha kinds this driver accepts.</summary>
    IReadOnlyList<CaptchaKind> Kinds { get; }

    Task<SolveResult> SolveAsync(NetClient http, CaptchaProviderConfig config, SolveRequest request,
        CancellationToken ct);

    Task<decimal?> GetBalanceAsync(NetClient http, CaptchaProviderConfig config,
        CancellationToken ct);
}

/// <summary>
/// Human Presence — <c>https://api.humanpresence.io/v2</c>. The binary carries the base URL
/// plus the v2 path, so this driver mirrors the site-key / action submission shape.
/// </summary>
public sealed class HumanPresenceDriver : ICaptchaDriver
{
    public const string BaseUrl = "https://api.humanpresence.io/v2";

    public string Type => "humanpresence";
    public string Name => "Human Presence";
    public bool BalanceSupported => true;
    public IReadOnlyList<CaptchaKind> Kinds => new[]
    {
        CaptchaKind.ReCaptcha, CaptchaKind.HCaptcha, CaptchaKind.Turnstile,
    };

    public async Task<SolveResult> SolveAsync(NetClient http, CaptchaProviderConfig config,
        SolveRequest request, CancellationToken ct)
    {
        var body = new JObject
        {
            ["clientKey"] = config.ApiKey,
            ["type"] = KindName(request.Kind),
            ["sitekey"] = request.SiteKey,
            ["pageurl"] = request.PageUrl,
            ["userAgent"] = request.UserAgent,
            ["proxy"] = request.Proxy,
            ["action"] = request.Action,
        };

        var started = DateTime.UtcNow;
        var res = await http.PostJsonAsync($"{BaseUrl}/solve", body.ToString(Formatting.None),
            Options(request.TimeoutSeconds), ct).ConfigureAwait(false);

        var elapsed = (DateTime.UtcNow - started).TotalSeconds;
        if (!res.IsSuccess)
            return Fail($"v2/solve HTTP {res.StatusCode}", elapsed);

        var root = TryParse(res.Body);
        var token = root?["token"]?.ToString() ?? root?["solution"]?["token"]?.ToString();
        return token is null
            ? Fail(root?["error"]?.ToString() ?? "no token", elapsed)
            : new SolveResult { Ok = true, Token = token, ElapsedSeconds = elapsed, Provider = Type };
    }

    public async Task<decimal?> GetBalanceAsync(NetClient http, CaptchaProviderConfig config,
        CancellationToken ct)
    {
        try
        {
            var o = Options(10);
            o.Headers["Authorization"] = "Bearer " + (config.ApiKey ?? string.Empty);
            var res = await http.GetAsync($"{BaseUrl}/balance", o, ct).ConfigureAwait(false);
            if (!res.IsSuccess) return null;

            var root = TryParse(res.Body);
            return root?["balance"]?.ToObject<decimal?>() ?? root?["credits"]?.ToObject<decimal?>();
        }
        catch (Exception)
        {
            return null;
        }
    }

    private static string KindName(CaptchaKind kind) => kind switch
    {
        CaptchaKind.ReCaptcha => "recaptcha_v2",
        CaptchaKind.HCaptcha => "hcaptcha",
        CaptchaKind.Turnstile => "turnstile",
        CaptchaKind.Geetest => "geetest",
        _ => "question",
    };

    internal static RequestOptions Options(double timeout) => new()
    {
        Timeout = TimeSpan.FromSeconds(Math.Max(15, timeout)),
        Tag = "captcha",
    };

    internal static SolveResult Fail(string error, double elapsed) =>
        new() { Ok = false, Error = error, ElapsedSeconds = elapsed };

    internal static JObject? TryParse(string body)
    {
        try { return JObject.Parse(body); }
        catch (JsonException) { return null; }
    }
}

/// <summary>Uncaptcha — <c>https://api.uncaptcha.io/v1</c>.</summary>
public sealed class UncaptchaDriver : ICaptchaDriver
{
    public const string BaseUrl = "https://api.uncaptcha.io/v1";

    public string Type => "uncaptcha";
    public string Name => "Uncaptcha";
    public bool BalanceSupported => true;
    public IReadOnlyList<CaptchaKind> Kinds => new[]
    {
        CaptchaKind.ReCaptcha, CaptchaKind.HCaptcha, CaptchaKind.Turnstile,
    };

    public async Task<SolveResult> SolveAsync(NetClient http, CaptchaProviderConfig config,
        SolveRequest request, CancellationToken ct)
    {
        var body = new JObject
        {
            ["apiKey"] = config.ApiKey,
            ["method"] = KindName(request.Kind),
            ["sitekey"] = request.SiteKey,
            ["pageurl"] = request.PageUrl,
            ["proxy"] = request.Proxy,
            ["userAgent"] = request.UserAgent,
            ["action"] = request.Action,
            ["invisible"] = 1,
        };

        var started = DateTime.UtcNow;
        var res = await http.PostJsonAsync($"{BaseUrl}/solve", body.ToString(Formatting.None),
            HumanPresenceDriver.Options(request.TimeoutSeconds), ct).ConfigureAwait(false);

        var elapsed = (DateTime.UtcNow - started).TotalSeconds;
        if (!res.IsSuccess)
            return HumanPresenceDriver.Fail($"v1/solve HTTP {res.StatusCode}", elapsed);

        var root = HumanPresenceDriver.TryParse(res.Body);
        var token = root?["request"]?.ToString() ?? root?["token"]?.ToString();

        // Uncaptcha is a task/poll provider: request holds the task id.
        if (root?["status"]?.ToString() == "1" && token is not null)
        {
            var solved = await PollAsync(http, config, token, request.TimeoutSeconds, ct)
                .ConfigureAwait(false);
            if (solved is not null)
                return new SolveResult
                {
                    Ok = true,
                    Token = solved,
                    ElapsedSeconds = (DateTime.UtcNow - started).TotalSeconds,
                    Provider = Type,
                };
        }

        return token is not null && root?["status"]?.ToString() == "1"
            ? HumanPresenceDriver.Fail("uncaptcha: polling never resolved", elapsed)
            : HumanPresenceDriver.Fail(root?["error"]?.ToString() ?? "uncaptcha: no task", elapsed);
    }

    private async Task<string?> PollAsync(NetClient http, CaptchaProviderConfig config,
        string taskId, double timeoutSeconds, CancellationToken ct)
    {
        var deadline = DateTimeOffset.UtcNow.AddSeconds(Math.Max(20, timeoutSeconds));
        while (DateTimeOffset.UtcNow < deadline)
        {
            ct.ThrowIfCancellationRequested();
            var url = $"{BaseUrl}/result?apiKey={Uri.EscapeDataString(config.ApiKey ?? string.Empty)}" +
                      $"&request={Uri.EscapeDataString(taskId)}";

            var res = await http.GetAsync(url, HumanPresenceDriver.Options(20), ct).ConfigureAwait(false);
            if (res.IsSuccess)
            {
                var root = HumanPresenceDriver.TryParse(res.Body);
                if (root?["status"]?.ToString() == "1")
                {
                    var token = root["request"]?.ToString();
                    if (!string.IsNullOrEmpty(token)) return token;
                }
            }
            await Task.Delay(TimeSpan.FromSeconds(2), ct).ConfigureAwait(false);
        }
        return null;
    }

    public async Task<decimal?> GetBalanceAsync(NetClient http, CaptchaProviderConfig config,
        CancellationToken ct)
    {
        try
        {
            var url = $"{BaseUrl}/balance?apiKey={Uri.EscapeDataString(config.ApiKey ?? string.Empty)}";
            var res = await http.GetAsync(url, HumanPresenceDriver.Options(10), ct).ConfigureAwait(false);
            if (!res.IsSuccess) return null;
            return HumanPresenceDriver.TryParse(res.Body)?["balance"]?.ToObject<decimal?>();
        }
        catch (Exception)
        {
            return null;
        }
    }

    private static string KindName(CaptchaKind kind) => kind switch
    {
        CaptchaKind.ReCaptcha => "userrecaptcha",
        CaptchaKind.HCaptcha => "hcaptcha",
        CaptchaKind.Turnstile => "turnstile",
        CaptchaKind.Geetest => "geetest",
        _ => "question",
    };
}

/// <summary>
/// Parallax Systems — <c>api.parallaxsystems.io/gen</c> plus the separate
/// <c>/holdcaptcha</c> endpoint the binary calls out by name.
/// </summary>
public sealed class ParallaxDriver : ICaptchaDriver
{
    public const string BaseUrl = "https://api.parallaxsystems.io";

    public string Type => "parallax";
    public string Name => "Parallax Systems";
    public bool BalanceSupported => true;
    public IReadOnlyList<CaptchaKind> Kinds => new[] { CaptchaKind.Turnstile, CaptchaKind.ReCaptcha };

    public async Task<SolveResult> SolveAsync(NetClient http, CaptchaProviderConfig config,
        SolveRequest request, CancellationToken ct)
    {
        var body = new JObject
        {
            ["key"] = config.ApiKey,
            ["sitekey"] = request.SiteKey,
            ["pageurl"] = request.PageUrl,
            ["proxy"] = request.Proxy,
            ["kind"] = request.Kind.ToString().ToLowerInvariant(),
        };

        var started = DateTime.UtcNow;
        var res = await http.PostJsonAsync($"{BaseUrl}/gen", body.ToString(Formatting.None),
            HumanPresenceDriver.Options(request.TimeoutSeconds), ct).ConfigureAwait(false);

        if (!res.IsSuccess)
            return HumanPresenceDriver.Fail($"gen HTTP {res.StatusCode}",
                (DateTime.UtcNow - started).TotalSeconds);

        var root = HumanPresenceDriver.TryParse(res.Body);
        var token = root?["token"]?.ToString() ?? root?["result"]?.ToString();
        if (!string.IsNullOrEmpty(token))
            return new SolveResult
            {
                Ok = true,
                Token = token,
                ElapsedSeconds = (DateTime.UtcNow - started).TotalSeconds,
                Provider = Type,
            };

        // Nothing available right now — ask them to hold the slot so a later retry is cheap.
        var hold = await HoldAsync(http, config, request, ct).ConfigureAwait(false);
        return HumanPresenceDriver.Fail(
            hold ?? root?["error"]?.ToString() ?? "parallax: no token",
            (DateTime.UtcNow - started).TotalSeconds);
    }

    /// <summary><c>HoldCaptchaEndpoint</c> — reserve a solve slot and return its handle.</summary>
    public async Task<string?> HoldAsync(NetClient http, CaptchaProviderConfig config,
        SolveRequest request, CancellationToken ct)
    {
        try
        {
            var body = new JObject
            {
                ["key"] = config.ApiKey,
                ["sitekey"] = request.SiteKey,
                ["pageurl"] = request.PageUrl,
            };

            var res = await http.PostJsonAsync($"{BaseUrl}/holdcaptcha", body.ToString(Formatting.None),
                HumanPresenceDriver.Options(15), ct).ConfigureAwait(false);
            if (!res.IsSuccess) return null;

            return HumanPresenceDriver.TryParse(res.Body)?["holdId"]?.ToString()
                   ?? HumanPresenceDriver.TryParse(res.Body)?["id"]?.ToString();
        }
        catch (Exception)
        {
            return null;
        }
    }

    public async Task<decimal?> GetBalanceAsync(NetClient http, CaptchaProviderConfig config,
        CancellationToken ct)
    {
        try
        {
            var res = await http.GetAsync($"{BaseUrl}/balance?key={Uri.EscapeDataString(config.ApiKey ?? string.Empty)}",
                HumanPresenceDriver.Options(10), ct).ConfigureAwait(false);
            if (!res.IsSuccess) return null;
            return HumanPresenceDriver.TryParse(res.Body)?["balance"]?.ToObject<decimal?>();
        }
        catch (Exception)
        {
            return null;
        }
    }
}

/// <summary>
/// Cybersole's own Cloudflare solver — <c>https://cf-solver.cybersole.io</c>
/// (Cybersole.CloudflareSolvers.CloudflareSolver).
/// </summary>
public sealed class CfSolverDriver : ICaptchaDriver
{
    public const string BaseUrl = "https://cf-solver.cybersole.io";

    public string Type => "cfsolver";
    public string Name => "Cybersole CF Solver";
    public bool BalanceSupported => true;
    public IReadOnlyList<CaptchaKind> Kinds => new[] { CaptchaKind.Turnstile };

    public async Task<SolveResult> SolveAsync(NetClient http, CaptchaProviderConfig config,
        SolveRequest request, CancellationToken ct)
    {
        var body = new JObject
        {
            ["token"] = config.ApiKey,
            ["sitekey"] = request.SiteKey,
            ["url"] = request.PageUrl,
            ["proxy"] = request.Proxy,
            ["userAgent"] = request.UserAgent,
            ["action"] = request.Action,
        };

        var started = DateTime.UtcNow;
        var res = await http.PostJsonAsync($"{BaseUrl}/solve", body.ToString(Formatting.None),
            HumanPresenceDriver.Options(request.TimeoutSeconds), ct).ConfigureAwait(false);

        var elapsed = (DateTime.UtcNow - started).TotalSeconds;
        if (!res.IsSuccess) return HumanPresenceDriver.Fail($"cf solve HTTP {res.StatusCode}", elapsed);

        var root = HumanPresenceDriver.TryParse(res.Body);
        var token = root?["token"]?.ToString() ?? root?["cf_clearance"]?.ToString();
        return string.IsNullOrEmpty(token)
            ? HumanPresenceDriver.Fail(root?["error"]?.ToString() ?? "cf solver: no token", elapsed)
            : new SolveResult { Ok = true, Token = token, ElapsedSeconds = elapsed, Provider = Type };
    }

    public async Task<decimal?> GetBalanceAsync(NetClient http, CaptchaProviderConfig config,
        CancellationToken ct)
    {
        try
        {
            var o = HumanPresenceDriver.Options(10);
            o.Headers["Authorization"] = "Bearer " + (config.ApiKey ?? string.Empty);
            var res = await http.GetAsync($"{BaseUrl}/balance", o, ct).ConfigureAwait(false);
            if (!res.IsSuccess) return null;
            return HumanPresenceDriver.TryParse(res.Body)?["balance"]?.ToObject<decimal?>();
        }
        catch (Exception)
        {
            return null;
        }
    }
}

/// <summary>
/// TwoCaptcha — the de-facto standard <c>in.php</c> / <c>res.php</c> pair, supported because
/// the settings page lets a user point at any compatible endpoint.
/// </summary>
public sealed class TwoCaptchaDriver : ICaptchaDriver
{
    public string Type => "twocaptcha";
    public string Name => "2Captcha";
    public bool BalanceSupported => true;
    public IReadOnlyList<CaptchaKind> Kinds => new[]
    {
        CaptchaKind.ReCaptcha, CaptchaKind.HCaptcha, CaptchaKind.Turnstile,
    };

    /// <summary>Overridable so a compatible mirror can be pointed at.</summary>
    public string BaseUrl { get; set; } = "https://2captcha.com";

    private string Base(CaptchaProviderConfig config) => BaseUrl;

    public async Task<SolveResult> SolveAsync(NetClient http, CaptchaProviderConfig config,
        SolveRequest request, CancellationToken ct)
    {
        var form = new Dictionary<string, string>
        {
            ["key"] = config.ApiKey ?? string.Empty,
            ["method"] = KindName(request.Kind),
            ["googlekey"] = request.SiteKey,
            ["pageurl"] = request.PageUrl,
            ["json"] = "1",
        };
        if (request.Action is not null) form["action"] = request.Action;
        if (request.Proxy is not null) form["proxy"] = request.Proxy;

        var started = DateTime.UtcNow;
        var res = await http.PostFormAsync($"{Base(config)}/in.php", form,
            HumanPresenceDriver.Options(request.TimeoutSeconds), ct).ConfigureAwait(false);

        if (!res.IsSuccess)
            return HumanPresenceDriver.Fail($"in.php HTTP {res.StatusCode}",
                (DateTime.UtcNow - started).TotalSeconds);

        var root = HumanPresenceDriver.TryParse(res.Body);
        if (root?["status"]?.ToString() == "0")
            return HumanPresenceDriver.Fail(
                root["request"]?.ToString() ?? "2captcha: submit rejected",
                (DateTime.UtcNow - started).TotalSeconds);

        var taskId = root?["request"]?.ToString();
        if (string.IsNullOrEmpty(taskId))
            return HumanPresenceDriver.Fail("2captcha: no task id",
                (DateTime.UtcNow - started).TotalSeconds);

        var deadline = DateTimeOffset.UtcNow.AddSeconds(Math.Max(20, request.TimeoutSeconds));
        while (DateTimeOffset.UtcNow < deadline)
        {
            ct.ThrowIfCancellationRequested();
            await Task.Delay(TimeSpan.FromSeconds(5), ct).ConfigureAwait(false);

            var poll = new Dictionary<string, string>
            {
                ["key"] = config.ApiKey ?? string.Empty,
                ["action"] = "get",
                ["id"] = taskId!,
                ["json"] = "1",
            };

            var pres = await http.PostFormAsync($"{Base(config)}/res.php", poll,
                HumanPresenceDriver.Options(20), ct).ConfigureAwait(false);
            if (!pres.IsSuccess) continue;

            var proot = HumanPresenceDriver.TryParse(pres.Body);
            var token = proot?["request"]?.ToString();
            if (!string.IsNullOrEmpty(token) && token != "CAPCHA_NOT_READY")
                return new SolveResult
                {
                    Ok = true,
                    Token = token,
                    ElapsedSeconds = (DateTime.UtcNow - started).TotalSeconds,
                    Provider = Type,
                };
        }

        return HumanPresenceDriver.Fail("2captcha: timeout",
            (DateTime.UtcNow - started).TotalSeconds);
    }

    public async Task<decimal?> GetBalanceAsync(NetClient http, CaptchaProviderConfig config,
        CancellationToken ct)
    {
        try
        {
            var form = new Dictionary<string, string>
            {
                ["key"] = config.ApiKey ?? string.Empty,
                ["action"] = "getbalance",
                ["json"] = "1",
            };
            var res = await http.PostFormAsync($"{Base(config)}/res.php", form,
                HumanPresenceDriver.Options(10), ct).ConfigureAwait(false);
            if (!res.IsSuccess) return null;
            var raw = HumanPresenceDriver.TryParse(res.Body)?["request"]?.ToString();
            return decimal.TryParse(raw, out var v) ? v : null;
        }
        catch (Exception)
        {
            return null;
        }
    }

    private static string KindName(CaptchaKind kind) => kind switch
    {
        CaptchaKind.ReCaptcha => "userrecaptcha",
        CaptchaKind.HCaptcha => "hcaptcha",
        CaptchaKind.Turnstile => "turnstile",
        _ => "userrecaptcha",
    };
}

/// <summary>Registry of every driver plus per-provider config rows.</summary>
public sealed class CaptchaProviderRegistry
{
    private readonly Dictionary<string, ICaptchaDriver> _drivers =
        new(StringComparer.OrdinalIgnoreCase);

    private readonly List<CaptchaProviderConfig> _configs = new();

    public IReadOnlyCollection<ICaptchaDriver> Drivers => _drivers.Values;
    public IReadOnlyList<CaptchaProviderConfig> Configs => _configs;

    public void Register(ICaptchaDriver driver) => _drivers[driver.Type] = driver;

    public void AddConfig(CaptchaProviderConfig config) => _configs.Add(config);

    public bool RemoveConfig(CaptchaProviderConfig config) => _configs.Remove(config);

    public ICaptchaDriver? Driver(string type) =>
        _drivers.TryGetValue(type, out var d) ? d : null;

    /// <summary>Highest-priority enabled provider that accepts this captcha kind.</summary>
    public CaptchaProviderConfig? SelectFor(CaptchaKind kind) =>
        _configs
            .Where(c => c.Enabled && c.ApiKey is { Length: > 0 })
            .Where(c => Driver(c.Type)?.Kinds.Contains(kind) == true)
            .OrderByDescending(c => c.Priority)
            .FirstOrDefault();

    public static CaptchaProviderRegistry CreateDefault()
    {
        var r = new CaptchaProviderRegistry();

        // Cybersole's own solver bridges. These are not what the real build lists under
        // Settings → 3rd Party Captcha Providers, but they are the services the binary talks
        // to directly (see docs/baseline/baseline_endpoints.txt).
        r.Register(new HumanPresenceDriver());
        r.Register(new UncaptchaDriver());
        r.Register(new ParallaxDriver());
        r.Register(new CfSolverDriver());

        // The seven entries the running 5.18.32 build actually offers in the Add Captcha
        // Provider dialog: 2Captcha, CapMonster, AntiCaptcha, AYCD, CapSolver, NextCaptcha,
        // SolveCaptcha. Read off the live window (docs/GUI_BASELINE.md).
        r.Register(new TwoCaptchaDriver());
        r.Register(new CapMonsterDriver());
        r.Register(new AntiCaptchaDriver());
        r.Register(new AycdCaptchaDriver());
        r.Register(new CapSolverDriver());
        r.Register(new NextCaptchaDriver());
        r.Register(new SolveCaptchaDriver());

        return r;
    }
}
