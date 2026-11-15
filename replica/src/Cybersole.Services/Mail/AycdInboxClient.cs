using System.Text.RegularExpressions;
using Cybersole.Core.Models;
using Cybersole.Http;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Cybersole.Services.Mail;

/// <summary>Outcome of a mailbox code lookup.</summary>
public sealed class MailCodeResult
{
    public bool Ok { get; init; }
    public string? Code { get; init; }
    public string? Subject { get; init; }
    public string? From { get; init; }
    public DateTimeOffset? Received { get; init; }
    public string? Error { get; init; }
    public string Source { get; init; } = "none";

    public static MailCodeResult Success(string code, string source, string? subject = null) =>
        new() { Ok = true, Code = code, Source = source, Subject = subject };

    public static MailCodeResult Fail(string error, string source) =>
        new() { Ok = false, Error = error, Source = source };
}

/// <summary>Request describing which mailbox to look in and which code to look for.</summary>
public sealed class MailCodeRequest
{
    public ImapAccount? Imap { get; init; }
    public AycdInbox? Aycd { get; init; }
    public string? Recipient { get; init; }
    public string? SenderContains { get; init; }
    public string? SubjectContains { get; init; }
    public DateTimeOffset? Since { get; init; }
    public TimeSpan Timeout { get; init; } = TimeSpan.FromMinutes(5);
    public TimeSpan PollInterval { get; init; } = TimeSpan.FromSeconds(3);
}

/// <summary>
/// AYCD Inbox client.
///
/// Endpoints below are the exact strings the binary carries:
/// <c>https://inbox-api.aycd.io/api/v1/tasks/mail/create</c>,
/// <c>https://inbox-api.aycd.io/api/v1/tasks/completed?group=</c>,
/// <c>https://inbox-api.aycd.io/api/v1/user/verify</c>.
/// </summary>
public sealed class AycdInboxClient
{
    public const string CreateUrl = "https://inbox-api.aycd.io/api/v1/tasks/mail/create";
    public const string CompletedUrl = "https://inbox-api.aycd.io/api/v1/tasks/completed?group=";
    public const string VerifyUrl = "https://inbox-api.aycd.io/api/v1/user/verify";

    private readonly NetClient _http;

    public AycdInboxClient(NetClient http) => _http = http;

    /// <summary>Validate an API key against <c>/user/verify</c>.</summary>
    public async Task<(bool Ok, string? Error, int? Credits)> VerifyAsync(string apiKey,
        CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(apiKey)) return (false, "empty api key", null);

        try
        {
            var res = await _http.GetAsync(VerifyUrl, Options(apiKey), ct).ConfigureAwait(false);
            if (!res.IsSuccess)
                return (false, $"verify HTTP {res.StatusCode}", null);

            var root = TryParse(res.Body);
            return (true, null, root?["credits"]?.ToObject<int?>() ?? root?["balance"]?.ToObject<int?>());
        }
        catch (Exception ex)
        {
            return (false, ex.Message, null);
        }
    }

    /// <summary>Create a mail task and return the task/group id to poll.</summary>
    public async Task<(bool Ok, string? TaskId, string? Error)> CreateTaskAsync(AycdInbox inbox,
        CancellationToken ct = default)
    {
        if (inbox.ApiKey is null) return (false, null, "no api key");

        var body = new JObject
        {
            ["templateId"] = inbox.TemplateId,
            ["group"] = inbox.AppGroup,
        };

        try
        {
            var res = await _http.PostJsonAsync(CreateUrl, body.ToString(Formatting.None),
                Options(inbox.ApiKey), ct).ConfigureAwait(false);

            if (!res.IsSuccess) return (false, null, $"create HTTP {res.StatusCode}");

            var root = TryParse(res.Body);
            var id = root?["id"]?.ToString()
                     ?? root?["taskId"]?.ToString()
                     ?? root?["group"]?.ToString();
            return string.IsNullOrEmpty(id)
                ? (false, null, "create returned no task id")
                : (true, id, null);
        }
        catch (Exception ex)
        {
            return (false, null, ex.Message);
        }
    }

    /// <summary>Pull completed mail tasks for a group.</summary>
    public async Task<(bool Ok, IReadOnlyList<JObject> Mails, string? Error)> GetCompletedAsync(
        string apiKey, string group, CancellationToken ct = default)
        => await GetCompletedAsyncVia(apiKey, group, BaseOrigin, ct).ConfigureAwait(false);

    /// <summary>Same as <see cref="GetCompletedAsync"/> with an explicit origin (tests / mirrors).</summary>
    public async Task<(bool Ok, IReadOnlyList<JObject> Mails, string? Error)> GetCompletedAsyncVia(
        string apiKey, string group, string origin, CancellationToken ct = default)
    {
        try
        {
            var url = $"{origin.TrimEnd('/')}/api/v1/tasks/completed?group={Uri.EscapeDataString(group)}";
            var res = await _http.GetAsync(url, Options(apiKey), ct).ConfigureAwait(false);

            if (!res.IsSuccess) return (false, Array.Empty<JObject>(), $"completed HTTP {res.StatusCode}");

            var root = TryParse(res.Body);
            var arr = root as JArray ?? root?["tasks"] as JArray ?? root?["data"] as JArray;
            var list = arr?.OfType<JObject>().ToList() ?? new List<JObject>();
            return (true, list, null);
        }
        catch (Exception ex)
        {
            return (false, Array.Empty<JObject>(), ex.Message);
        }
    }

    public const string BaseOrigin = "https://inbox-api.aycd.io";

    /// <summary>Poll until a code shows up in a completed mail, or the timeout expires.</summary>
    public async Task<MailCodeResult> WaitForCodeAsync(MailCodeRequest request,
        CancellationToken ct = default)
    {
        var inbox = request.Aycd;
        if (inbox?.ApiKey is null) return MailCodeResult.Fail("no aycd api key", "aycd");

        var budget = request.Timeout;
        if (inbox.TimeoutSeconds > 0) budget = TimeSpan.FromSeconds(inbox.TimeoutSeconds);
        var deadline = DateTimeOffset.UtcNow + budget;

        var group = inbox.AppGroup;
        if (string.IsNullOrEmpty(group))
        {
            var created = await CreateTaskAsync(inbox, ct).ConfigureAwait(false);
            if (!created.Ok) return MailCodeResult.Fail(created.Error ?? "create failed", "aycd");
            group = created.TaskId;
        }

        while (DateTimeOffset.UtcNow < deadline)
        {
            ct.ThrowIfCancellationRequested();

            var (ok, mails, error) = await GetCompletedAsync(inbox.ApiKey!, group!, ct)
                .ConfigureAwait(false);
            if (!ok && error is not null)
                return MailCodeResult.Fail(error, "aycd");

            foreach (var mail in mails)
            {
                var body = mail["body"]?.ToString() ?? mail["html"]?.ToString() ?? string.Empty;
                var subject = mail["subject"]?.ToString() ?? string.Empty;
                if (!MatchesSender(mail["from"]?.ToString(), request)) continue;

                var code = VerificationCodeExtractor.Extract(subject + "\n" + body);
                if (code is not null)
                    return MailCodeResult.Success(code, "aycd", subject);
            }

            await Task.Delay(request.PollInterval, ct).ConfigureAwait(false);
        }

        return MailCodeResult.Fail("timeout waiting for code", "aycd");
    }

    private static bool MatchesSender(string? from, MailCodeRequest request)
    {
        if (from is null) return true;
        if (!string.IsNullOrEmpty(request.SenderContains) &&
            !from.Contains(request.SenderContains!, StringComparison.OrdinalIgnoreCase))
            return false;
        return true;
    }

    private static RequestOptions Options(string apiKey)
    {
        var o = new RequestOptions
        {
            Timeout = TimeSpan.FromSeconds(20),
            Tag = "aycd-inbox",
        };
        o.Headers["Authorization"] = "Bearer " + apiKey;
        o.Headers["X-Api-Key"] = apiKey;
        return o;
    }

    private static JToken? TryParse(string body)
    {
        try { return JToken.Parse(body); }
        catch (JsonException) { return null; }
    }
}

/// <summary>
/// Pulls 4–8 digit verification codes out of a mail body while rejecting the numbers that
/// look like money, order ids, tracking numbers or years.
/// </summary>
public static class VerificationCodeExtractor
{
    private static readonly string[] StrongKeywords =
    {
        "verification code", "verify", "one-time", "one time", "otp", "passcode",
        "security code", "confirmation code", "your code", "code is", "code:",
        "验证码", "驗證碼", "コード", "인증번호", "código", "code de vérification",
    };

    private static readonly string[] WeakKeywords =
    {
        "code", "pin", "token",
    };

    private static readonly Regex CodePattern = new(
        @"(?<![0-9A-Za-z])(\d{4,8})(?![0-9A-Za-z])",
        RegexOptions.Compiled);

    private static readonly Regex MoneyPattern = new(
        @"[$€£¥]\s?\d|\d+[.,]\d{2}\b",
        RegexOptions.Compiled);

    private static readonly Regex OrderPattern = new(
        @"(?:order|invoice|reference|ref|tracking|sku|model)\s*[:#]?\s*[A-Z0-9\-]{4,}",
        RegexOptions.Compiled | RegexOptions.IgnoreCase);

    /// <summary>Extract the most likely code, or null when none looks like one.</summary>
    public static string? Extract(string? text)
    {
        if (string.IsNullOrWhiteSpace(text)) return null;

        var stripped = StripHtml(text);
        var lowered = stripped.ToLowerInvariant();

        var strongHit = StrongKeywords.Any(k => lowered.Contains(k, StringComparison.Ordinal));
        var weakHit = WeakKeywords.Any(k => lowered.Contains(k, StringComparison.Ordinal));

        // Remove the segments where a plausible number would be a price or an order number.
        var cleaned = MoneyPattern.Replace(stripped, " ");
        cleaned = OrderPattern.Replace(cleaned, " ");

        var candidates = new List<(string Code, int Score)>();
        foreach (Match m in CodePattern.Matches(cleaned))
        {
            var code = m.Groups[1].Value;
            var score = 0;

            if (strongHit) score += 4;
            else if (weakHit) score += 1;

            // Proximity to a keyword is the strongest signal.
            var window = WindowAround(cleaned, m.Index, 60).ToLowerInvariant();
            if (StrongKeywords.Any(k => window.Contains(k, StringComparison.Ordinal))) score += 5;
            else if (WeakKeywords.Any(k => window.Contains(k, StringComparison.Ordinal))) score += 2;

            // A 6-digit code is the most common shape.
            score += code.Length switch { 6 => 3, 5 or 7 => 2, 4 => 1, _ => 0 };

            // Reject years and obvious non-codes.
            var numeric = int.Parse(code);
            if (code.Length == 4 && numeric is >= 1900 and <= 2100) score -= 6;
            if (code.Length >= 7 && code.StartsWith("000")) score -= 3;

            candidates.Add((code, score));
        }

        var best = candidates.OrderByDescending(c => c.Score).FirstOrDefault();
        return best.Score > 0 ? best.Code : null;
    }

    private static string WindowAround(string text, int index, int radius)
    {
        var start = Math.Max(0, index - radius);
        var end = Math.Min(text.Length, index + radius);
        return text[start..end];
    }

    private static string StripHtml(string html)
    {
        if (!html.Contains('<')) return html;
        var noTags = Regex.Replace(html, "<[^>]+>", " ");
        return System.Net.WebUtility.HtmlDecode(noTags);
    }
}
