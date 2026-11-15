using Cybersole.Core.Store;
using Cybersole.Http;

namespace Cybersole.Services.Captcha;

public enum CaptchaKind { ReCaptcha, HCaptcha, Turnstile, Geetest, Question }

public sealed class SolveRequest
{
    public CaptchaKind Kind { get; init; } = CaptchaKind.Turnstile;
    public required string SiteKey { get; init; }
    public required string PageUrl { get; init; }
    public string? Proxy { get; init; }
    public string? UserAgent { get; init; }
    public string? Action { get; init; }
    public double TimeoutSeconds { get; init; } = 60;
}

public sealed class SolveResult
{
    public bool Ok { get; init; }
    public string? Token { get; init; }
    public double ElapsedSeconds { get; init; }
    public decimal Cost { get; init; }
    public string? Provider { get; init; }
    public string? Error { get; init; }
}

/// <summary>
/// Captcha solving gateway (Cybersole.Services.Captcha).
/// Supports the built-in solver view plus external providers
/// (Uncaptcha / Parallax / Cybersole CF solver), matching the endpoints found in the binary.
/// </summary>
public sealed class CaptchaSolverService
{
    public const string UncaptchaUrl = "https://api.uncaptcha.io/v1";
    public const string ParallaxUrl = "https://api.parallaxsystems.io";
    public const string CfSolverUrl = "https://cf-solver.cybersole.io";

    private readonly NetClient _http;
    private readonly EventBus _bus;

    public CaptchaSolverService(NetClient http, EventBus bus)
    {
        _http = http;
        _bus = bus;
    }

    public string Provider { get; set; } = "internal";
    public string? ApiKey { get; set; }
    public int Concurrency { get; set; } = 10;

    /// <summary>Multi-provider registry; when it has a matching config the driver is used.</summary>
    public CaptchaProviderRegistry Registry { get; } = CaptchaProviderRegistry.CreateDefault();

    public async Task<SolveResult> SolveAsync(SolveRequest request, CancellationToken ct = default)
    {
        var started = DateTime.UtcNow;

        // Prefer a configured driver from the registry (priority order), else fall back to
        // the legacy provider switch below.
        var config = Registry.SelectFor(request.Kind);
        var driver = config is null ? null : Registry.Driver(config.Type);
        if (driver is not null && config is not null)
        {
            try
            {
                config.IsFetchingBalance = false;
                var solved = await driver.SolveAsync(_http, config, request, ct).ConfigureAwait(false);
                if (solved.Ok)
                {
                    config.Count++;
                    return new SolveResult
                    {
                        Ok = true,
                        Token = solved.Token,
                        ElapsedSeconds = solved.ElapsedSeconds,
                        Cost = solved.Cost,
                        Provider = driver.Type,
                    };
                }
                _bus.Error("Captcha", $"{driver.Type}: {solved.Error}");
            }
            catch (Exception ex)
            {
                _bus.Error("Captcha", $"{driver.Type} threw: {ex.Message}");
            }
        }

        try
        {
            var (endpoint, payload) = BuildRequest(request);
            var res = await _http.PostJsonAsync(endpoint, payload,
                new RequestOptions { Tag = "captcha", Timeout = TimeSpan.FromSeconds(request.TimeoutSeconds) },
                ct).ConfigureAwait(false);

            var elapsed = (DateTime.UtcNow - started).TotalSeconds;
            if (!res.IsSuccess)
                return new SolveResult { Ok = false, Error = $"HTTP {res.StatusCode}", ElapsedSeconds = elapsed };

            var body = Newtonsoft.Json.Linq.JObject.Parse(res.Body);
            var token = body["token"]?.ToString() ?? body["solution"]?.ToString() ?? body["gRecaptchaResponse"]?.ToString();
            return new SolveResult
            {
                Ok = !string.IsNullOrEmpty(token),
                Token = token,
                ElapsedSeconds = elapsed,
                Provider = Provider,
                Error = string.IsNullOrEmpty(token) ? body["error"]?.ToString() : null,
            };
        }
        catch (Exception ex)
        {
            _bus.Error("Captcha", $"solve failed: {ex.Message}");
            return new SolveResult { Ok = false, Error = ex.Message,
                ElapsedSeconds = (DateTime.UtcNow - started).TotalSeconds };
        }
    }

    private (string endpoint, string payload) BuildRequest(SolveRequest r)
    {
        var type = Provider switch
        {
            "uncaptcha" => "uncaptcha",
            "parallax" => "parallax",
            "cfsolver" => "cf",
            _ => "internal",
        };

        var endpoint = Provider switch
        {
            "uncaptcha" => $"{UncaptchaUrl}/solve",
            "parallax" => $"{ParallaxUrl}/gen",
            "cfsolver" => $"{CfSolverUrl}/solve",
            _ => "http://127.0.0.1:8191/solve",
        };

        var payload = Newtonsoft.Json.JsonConvert.SerializeObject(new
        {
            kind = r.Kind.ToString().ToLowerInvariant(),
            sitekey = r.SiteKey,
            url = r.PageUrl,
            proxy = r.Proxy,
            userAgent = r.UserAgent,
            action = r.Action,
            type,
            apiKey = ApiKey,
            timeout = (int)r.TimeoutSeconds,
        });

        return (endpoint, payload);
    }
}
