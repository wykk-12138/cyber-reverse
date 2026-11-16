using Cybersole.Http;
using Newtonsoft.Json.Linq;

namespace Cybersole.Services.Captcha;

/// <summary>
/// Shared shape for the JSON "task" captcha APIs — createTask returns a taskId, then
/// getTaskResult is polled until it reports ready.
///
/// The running 5.18.32 build offers AntiCaptcha, CapMonster, CapSolver and NextCaptcha in
/// Settings → 3rd Party Captcha Providers; all four speak this protocol with the same field
/// names, so one driver class parameterised on the endpoint serves all of them.
/// </summary>
public abstract class TaskApiDriver : ICaptchaDriver
{
    public abstract string Type { get; }
    public abstract string Name { get; }
    public abstract string BaseUrl { get; }

    public bool BalanceSupported => true;

    public IReadOnlyList<CaptchaKind> Kinds => new[]
    {
        CaptchaKind.ReCaptcha, CaptchaKind.HCaptcha, CaptchaKind.Turnstile,
    };

    public async Task<SolveResult> SolveAsync(NetClient http, CaptchaProviderConfig config,
        SolveRequest request, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(config.ApiKey))
            return Fail("no api key");

        var task = new JObject
        {
            ["type"] = TaskType(request.Kind),
            ["websiteURL"] = request.PageUrl,
            ["websiteKey"] = request.SiteKey,
        };
        if (!string.IsNullOrEmpty(request.Action)) task["pageAction"] = request.Action;
        if (!string.IsNullOrEmpty(request.UserAgent)) task["userAgent"] = request.UserAgent;
        if (!string.IsNullOrEmpty(request.Proxy)) task["proxy"] = request.Proxy;

        var create = new JObject
        {
            ["clientKey"] = config.ApiKey,
            ["task"] = task,
        };

        var created = await http.PostJsonAsync(BaseUrl + "/createTask", create.ToString(),
            new RequestOptions { Tag = "captcha-create" }, ct).ConfigureAwait(false);

        if (!created.IsSuccess)
            return Fail($"{Name} createTask HTTP {created.StatusCode}");

        var createdBody = JObject.Parse(created.Body);
        if (createdBody["errorId"]?.Value<int>() is > 0)
            return Fail($"{Name}: {createdBody["errorDescription"]}");

        var taskId = createdBody["taskId"]?.ToString();
        if (string.IsNullOrEmpty(taskId))
            return Fail($"{Name}: createTask returned no taskId");

        // poll — these APIs answer "processing" for a few seconds before a token appears
        for (var attempt = 0; attempt < 30; attempt++)
        {
            await Task.Delay(1000, ct).ConfigureAwait(false);

            var poll = new JObject
            {
                ["clientKey"] = config.ApiKey,
                ["taskId"] = taskId,
            };

            var status = await http.PostJsonAsync(BaseUrl + "/getTaskResult", poll.ToString(),
                new RequestOptions { Tag = "captcha-poll" }, ct).ConfigureAwait(false);

            if (!status.IsSuccess) continue;

            var body = JObject.Parse(status.Body);
            if (body["errorId"]?.Value<int>() is > 0)
                return Fail($"{Name}: {body["errorDescription"]}");

            if (body["status"]?.ToString() == "ready")
            {
                var token = body["solution"]?["gRecaptchaResponse"]?.ToString()
                            ?? body["solution"]?["token"]?.ToString();
                return string.IsNullOrEmpty(token)
                    ? Fail($"{Name}: ready but no token")
                    : new SolveResult { Ok = true, Token = token, Provider = Name };
            }
        }

        return Fail($"{Name}: timed out waiting for a token");
    }

    public async Task<decimal?> GetBalanceAsync(NetClient http, CaptchaProviderConfig config,
        CancellationToken ct)
    {
        if (string.IsNullOrEmpty(config.ApiKey)) return null;

        try
        {
            var req = new JObject { ["clientKey"] = config.ApiKey };
            var res = await http.PostJsonAsync(BaseUrl + "/getBalance", req.ToString(),
                new RequestOptions { Tag = "captcha-balance" }, ct).ConfigureAwait(false);

            if (!res.IsSuccess) return null;

            var body = JObject.Parse(res.Body);
            return body["balance"]?.Value<decimal?>();
        }
        catch
        {
            return null;
        }
    }

    private static SolveResult Fail(string error) =>
        new() { Ok = false, Error = error };

    private static string TaskType(CaptchaKind kind) => kind switch
    {
        CaptchaKind.ReCaptcha => "NoCaptchaTaskProxyless",
        CaptchaKind.HCaptcha => "HCaptchaTaskProxyless",
        CaptchaKind.Turnstile => "TurnstileTaskProxyless",
        _ => "NoCaptchaTaskProxyless",
    };
}

/// <summary>AntiCaptcha — <c>https://api.anti-captcha.com</c>.</summary>
public sealed class AntiCaptchaDriver : TaskApiDriver
{
    public override string Type => "anticaptcha";
    public override string Name => "AntiCaptcha";
    public override string BaseUrl => "https://api.anti-captcha.com";
}

/// <summary>CapMonster Cloud — <c>https://api.capmonster.cloud</c>.</summary>
public sealed class CapMonsterDriver : TaskApiDriver
{
    public override string Type => "capmonster";
    public override string Name => "CapMonster";
    public override string BaseUrl => "https://api.capmonster.cloud";
}

/// <summary>CapSolver — <c>https://api.capsolver.com</c>.</summary>
public sealed class CapSolverDriver : TaskApiDriver
{
    public override string Type => "capsolver";
    public override string Name => "CapSolver";
    public override string BaseUrl => "https://api.capsolver.com";
}

/// <summary>NextCaptcha — <c>https://api.nextcaptcha.com</c>.</summary>
public sealed class NextCaptchaDriver : TaskApiDriver
{
    public override string Type => "nextcaptcha";
    public override string Name => "NextCaptcha";
    public override string BaseUrl => "https://api.nextcaptcha.com";
}

/// <summary>
/// SolveCaptcha — <c>https://api.solvecaptcha.com</c>. Unlike the others it keeps the older
/// form-encoded in.php / res.php surface, so it cannot reuse <see cref="TaskApiDriver"/>.
/// </summary>
public sealed class SolveCaptchaDriver : ICaptchaDriver
{
    public const string BaseUrl = "https://api.solvecaptcha.com";

    public string Type => "solvecaptcha";
    public string Name => "SolveCaptcha";
    public bool BalanceSupported => true;

    public IReadOnlyList<CaptchaKind> Kinds => new[]
    {
        CaptchaKind.ReCaptcha, CaptchaKind.HCaptcha,
    };

    public async Task<SolveResult> SolveAsync(NetClient http, CaptchaProviderConfig config,
        SolveRequest request, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(config.ApiKey)) return Fail("no api key");

        var form = new Dictionary<string, string>
        {
            ["key"] = config.ApiKey!,
            ["method"] = request.Kind == CaptchaKind.HCaptcha ? "hcaptcha" : "userrecaptcha",
            ["googlekey"] = request.SiteKey ?? string.Empty,
            ["pageurl"] = request.PageUrl ?? string.Empty,
            ["json"] = "1",
        };
        if (!string.IsNullOrEmpty(request.Action)) form["action"] = request.Action!;

        var created = await http.PostFormAsync(BaseUrl + "/in.php", form,
            new RequestOptions { Tag = "solvecaptcha-create" }, ct).ConfigureAwait(false);

        if (!created.IsSuccess)
            return Fail($"SolveCaptcha in.php HTTP {created.StatusCode}");

        var createdBody = JObject.Parse(created.Body);
        if (createdBody["status"]?.Value<int>() != 1)
            return Fail($"SolveCaptcha: {createdBody["request"]}");

        var id = createdBody["request"]?.ToString();
        if (string.IsNullOrEmpty(id)) return Fail("SolveCaptcha: no request id");

        for (var attempt = 0; attempt < 30; attempt++)
        {
            await Task.Delay(1000, ct).ConfigureAwait(false);

            var poll = await http.GetAsync(
                $"{BaseUrl}/res.php?key={Uri.EscapeDataString(config.ApiKey!)}&action=get&id={id}&json=1",  // inferred: no image evidence (R298)
                new RequestOptions { Tag = "solvecaptcha-poll" }, ct).ConfigureAwait(false);

            if (!poll.IsSuccess) continue;

            var body = JObject.Parse(poll.Body);
            if (body["status"]?.Value<int>() == 1)
            {
                var token = body["request"]?.ToString();
                return string.IsNullOrEmpty(token)
                    ? Fail("SolveCaptcha: empty token")
                    : new SolveResult { Ok = true, Token = token, Provider = Name };
            }

            if (body["request"]?.ToString() is { } msg &&
                msg.Contains("ERROR", StringComparison.OrdinalIgnoreCase))
                return Fail($"SolveCaptcha: {msg}");
        }

        return Fail("SolveCaptcha: timed out");
    }

    public async Task<decimal?> GetBalanceAsync(NetClient http, CaptchaProviderConfig config,
        CancellationToken ct)
    {
        if (string.IsNullOrEmpty(config.ApiKey)) return null;

        try
        {
            var res = await http.GetAsync(
                $"{BaseUrl}/res.php?key={Uri.EscapeDataString(config.ApiKey!)}&action=getbalance&json=1",  // inferred: no image evidence (R298)
                new RequestOptions { Tag = "solvecaptcha-balance" }, ct).ConfigureAwait(false);

            if (!res.IsSuccess) return null;

            var body = JObject.Parse(res.Body);
            return decimal.TryParse(body["request"]?.ToString(),
                System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var v) ? v : null;
        }
        catch
        {
            return null;
        }
    }

    private static SolveResult Fail(string error) =>
        new() { Ok = false, Error = error };
}

/// <summary>
/// AYCD — the real build lists it as a captcha provider, but AYCD is a local automation bridge
/// rather than a token service: it exposes a REST inbox on the machine. This driver reports
/// honestly instead of pretending to solve.
/// </summary>
public sealed class AycdCaptchaDriver : ICaptchaDriver
{
    public string Type => "aycd";
    public string Name => "AYCD";
    public bool BalanceSupported => false;

    public IReadOnlyList<CaptchaKind> Kinds => Array.Empty<CaptchaKind>();

    public Task<SolveResult> SolveAsync(NetClient http, CaptchaProviderConfig config,
        SolveRequest request, CancellationToken ct) =>
        Task.FromResult(new SolveResult
        {
            Ok = false,
            Error = "AYCD is an inbox bridge, not a token service",
        });

    public Task<decimal?> GetBalanceAsync(NetClient http, CaptchaProviderConfig config,
        CancellationToken ct) => Task.FromResult<decimal?>(null);
}
