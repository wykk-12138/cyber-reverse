using System.Text.RegularExpressions;
using Cybersole.Core.Models;
using Cybersole.Http;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Cybersole.Services.Mail;

public enum MailFilterTarget
{
    Subject = 0,
    From = 1,
    Body = 2,
}

public enum MailFilterComparator
{
    Includes = 0,
    Excludes = 1,
    Matches = 2,
}

public enum MailElementType
{
    Text = 0,
    Html = 1,
    Link = 2,
    Numeric = 3,
}

public sealed class MailFilter
{
    public MailFilterTarget Target { get; init; } = MailFilterTarget.Subject;
    public MailFilterComparator Comparator { get; init; } = MailFilterComparator.Includes;
    public string? Value { get; init; }
    public IReadOnlyList<string>? OrValues { get; init; }
    public bool Optional { get; init; }
    public bool RawHtml { get; init; }
}

public sealed class MailElement
{
    public required string Name { get; init; }
    public MailFilterTarget Target { get; init; } = MailFilterTarget.Body;
    public MailElementType Type { get; init; } = MailElementType.Numeric;
    public string? Selector { get; init; }
    public string? Regex { get; init; }
    public string? RegexSource { get; init; }
    public string? Formatter { get; init; }
    public bool Optional { get; init; }
    public bool RawHtml { get; init; }
}

public sealed record MailMessageSnapshot(
    string? Subject,
    IReadOnlyList<string> From,
    IReadOnlyList<string> To,
    string? TextBody,
    string? HtmlBody,
    DateTimeOffset Date);

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
    public IReadOnlyDictionary<string, string> Values { get; init; } = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

    public static MailCodeResult Success(
        string code,
        string source,
        string? subject = null,
        IReadOnlyDictionary<string, string>? values = null) =>
        new()
        {
            Ok = true,
            Code = code,
            Source = source,
            Subject = subject,
            Values = values ?? new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase),
        };

    public static MailCodeResult Fail(string error, string source) =>
        new() { Ok = false, Error = error, Source = source };
}

/// <summary>Request describing which mailbox to look in and which code to look for.</summary>
public sealed class MailCodeRequest
{
    public ImapAccount? Imap { get; init; }
    public IReadOnlyList<ImapAccount>? ImapAccounts { get; init; }
    public AycdInbox? Aycd { get; init; }
    public string? Recipient { get; init; }
    public string? SenderContains { get; init; }
    public string? SubjectContains { get; init; }
    public IReadOnlyList<MailFilter> Filters { get; init; } = Array.Empty<MailFilter>();
    public IReadOnlyList<MailElement> Elements { get; init; } = Array.Empty<MailElement>();
    public bool AllowMultiple { get; init; }
    public DateTimeOffset? Since { get; init; }
    public TimeSpan Timeout { get; init; } = TimeSpan.FromMinutes(5);
    public TimeSpan PollInterval { get; init; } = TimeSpan.FromSeconds(3);
    public string? AycdBaseOriginOverride { get; init; }
}

/// <summary>
/// AYCD Inbox client matching the binary's <c>AycdInboxService</c>:
/// endpoints <c>/api/v1/tasks/mail/create</c>, <c>/api/v1/tasks/completed?group=</c>,
/// <c>/api/v1/user/verify</c>, <c>Authorization: Token &lt;apiKey&gt;</c>, <c>Timeout=30s</c>,
/// <c>AllowAutoRedirect=false</c>, and camelCase create/completed JSON schemas.
/// </summary>
public sealed class AycdInboxClient
{
    public const string BaseOrigin = "https://inbox-api.aycd.io";
    public const string CreateUrl = "https://inbox-api.aycd.io/api/v1/tasks/mail/create";
    public const string CompletedUrl = "https://inbox-api.aycd.io/api/v1/tasks/completed?group=";
    public const string VerifyUrl = "https://inbox-api.aycd.io/api/v1/user/verify";

    public static readonly TimeSpan NormalPollInterval = TimeSpan.FromSeconds(3);
    public static readonly TimeSpan BurstPollInterval = TimeSpan.FromSeconds(1);
    public static readonly TimeSpan IdleSleepInterval = TimeSpan.FromSeconds(1);
    public static readonly TimeSpan MaxPendingLifetime = TimeSpan.FromSeconds(600);

    private readonly NetClient _http;

    public AycdInboxClient(NetClient http) => _http = http;

    /// <summary>Validate an API key against <c>/api/v1/user/verify</c>.</summary>
    public Task<(bool Ok, string? Error, int? Credits)> VerifyAsync(string apiKey, CancellationToken ct = default)
        => VerifyAsync(apiKey, BaseOrigin, ct);

    public async Task<(bool Ok, string? Error, int? Credits)> VerifyAsync(string apiKey, string origin,
        CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(apiKey)) return (false, "empty api key", null);

        try
        {
            var url = $"{origin.TrimEnd('/')}/api/v1/user/verify";
            var res = await _http.GetAsync(url, Options(apiKey), ct).ConfigureAwait(false);
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
    public Task<(bool Ok, string? TaskId, string? Error)> CreateTaskAsync(AycdInbox inbox,
        CancellationToken ct = default)
        => CreateTaskAsync(inbox, request: null, origin: BaseOrigin, ct);

    public async Task<(bool Ok, string? TaskId, string? Error)> CreateTaskAsync(
        AycdInbox inbox,
        MailCodeRequest? request,
        string origin = BaseOrigin,
        CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(inbox.ApiKey)) return (false, null, "no api key");

        var timeoutSec = inbox.TimeoutSeconds > 0
            ? inbox.TimeoutSeconds
            : (int)(request?.Timeout.TotalSeconds ?? 600);
        timeoutSec = Math.Clamp(timeoutSec, 1, 3600);

        var filters = BuildWireFilters(request);
        var elements = BuildWireElements(request);
        var group = !string.IsNullOrWhiteSpace(inbox.AppGroup)
            ? inbox.AppGroup
            : "cybersole-" + SanitizeGroup(request?.Recipient ?? "default");

        var body = new JObject
        {
            ["templateId"] = inbox.TemplateId,
            ["group"] = group,
            ["email"] = request?.Recipient,
            ["receivedAt"] = (request?.Since ?? DateTimeOffset.UtcNow).ToUnixTimeSeconds(),
            ["mailFilters"] = filters,
            ["mailElements"] = elements,
            ["timeout"] = timeoutSec,
        };

        try
        {
            var url = $"{origin.TrimEnd('/')}/api/v1/tasks/mail/create";
            var res = await _http.PostJsonAsync(url, body.ToString(Formatting.None),
                Options(inbox.ApiKey!), ct).ConfigureAwait(false);

            if (!res.IsSuccess) return (false, null, $"create HTTP {res.StatusCode}");

            var root = TryParse(res.Body);
            var id = root?["id"]?.ToString()
                     ?? root?["taskId"]?.ToString()
                     ?? root?["group"]?.ToString();
            return string.IsNullOrEmpty(id)
                ? (false, null, "No task ID returned")
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

    /// <summary>Poll until a code shows up in a completed mail, or the timeout expires.</summary>
    public async Task<MailCodeResult> WaitForCodeAsync(MailCodeRequest request,
        CancellationToken ct = default)
    {
        var inbox = request.Aycd;
        if (inbox?.ApiKey is null || string.IsNullOrWhiteSpace(inbox.ApiKey))
            return MailCodeResult.Fail("no aycd api key", "aycd");

        var origin = string.IsNullOrWhiteSpace(request.AycdBaseOriginOverride)
            ? BaseOrigin
            : request.AycdBaseOriginOverride!;

        var budget = request.Timeout;
        if (inbox.TimeoutSeconds > 0 && request.Timeout == TimeSpan.FromMinutes(5))
            budget = TimeSpan.FromSeconds(Math.Clamp(inbox.TimeoutSeconds, 1, (int)MaxPendingLifetime.TotalSeconds));
        var deadline = DateTimeOffset.UtcNow + budget;

        var group = inbox.AppGroup;
        string? createdTaskId = null;
        if (string.IsNullOrEmpty(group))
        {
            var created = await CreateTaskAsync(inbox, request, origin, ct).ConfigureAwait(false);
            if (!created.Ok) return MailCodeResult.Fail(created.Error ?? "create failed", "aycd");
            createdTaskId = created.TaskId;
            group = createdTaskId;
        }

        while (DateTimeOffset.UtcNow < deadline)
        {
            ct.ThrowIfCancellationRequested();

            var (ok, mails, error) = await GetCompletedAsyncVia(inbox.ApiKey!, group!, origin, ct)
                .ConfigureAwait(false);
            if (!ok && error is not null)
                return MailCodeResult.Fail(error, "aycd");

            foreach (var mail in mails)
            {
                var taskId = mail["id"]?.ToString();
                if (!string.IsNullOrEmpty(createdTaskId) && !string.IsNullOrEmpty(taskId) &&
                    !string.Equals(createdTaskId, taskId, StringComparison.Ordinal) &&
                    !string.Equals(createdTaskId, group, StringComparison.Ordinal))
                    continue;

                if (mail["results"] is JObject resultsObj && resultsObj.HasValues)
                {
                    var dict = resultsObj.Properties()
                        .Where(p => p.Value.Type != JTokenType.Null)
                        .ToDictionary(p => p.Name, p => p.Value.ToString(), StringComparer.OrdinalIgnoreCase);

                    var primary = dict.TryGetValue("code", out var explicitCode) && !string.IsNullOrEmpty(explicitCode)
                        ? explicitCode
                        : dict.Values.FirstOrDefault(v => !string.IsNullOrEmpty(v));
                    if (!string.IsNullOrEmpty(primary))
                        return MailCodeResult.Success(primary!, "aycd", mail["subject"]?.ToString(), dict);
                }

                var body = mail["body"]?.ToString() ?? mail["html"]?.ToString() ?? string.Empty;
                var subject = mail["subject"]?.ToString() ?? string.Empty;
                var from = mail["from"]?.ToString();
                var snap = new MailMessageSnapshot(
                    subject,
                    string.IsNullOrEmpty(from) ? Array.Empty<string>() : new[] { from! },
                    Array.Empty<string>(),
                    body,
                    mail["html"]?.ToString(),
                    request.Since ?? DateTimeOffset.UtcNow);

                var matched = MailMessageMatcher.EvaluateMessage(snap, request, "aycd");
                if (matched is { Ok: true })
                    return matched;
            }

            var delay = mails.Count >= 100
                ? BurstPollInterval
                : (request.PollInterval > TimeSpan.Zero ? request.PollInterval : NormalPollInterval);
            await Task.Delay(delay, ct).ConfigureAwait(false);
        }

        return MailCodeResult.Fail("timeout waiting for code", "aycd");
    }

    private static JArray BuildWireFilters(MailCodeRequest? request)
    {
        var arr = new JArray();
        if (request is null) return arr;

        foreach (var f in MailMessageMatcher.EffectiveFilters(request))
        {
            var obj = new JObject
            {
                ["target"] = WireTarget(f.Target),
                ["comparator"] = WireComparator(f.Comparator),
                ["value"] = f.Value ?? string.Empty,
                ["optional"] = f.Optional,
            };
            if (f.OrValues is { Count: > 0 })
                obj["orValues"] = new JArray(f.OrValues);
            arr.Add(obj);
        }
        return arr;
    }

    private static JArray BuildWireElements(MailCodeRequest? request)
    {
        var arr = new JArray();
        if (request is null) return arr;

        foreach (var el in request.Elements)
        {
            arr.Add(new JObject
            {
                ["name"] = el.Name,
                ["target"] = WireTarget(el.Target),
                ["selector"] = el.Selector,
                ["regex"] = el.Regex,
                ["regexSource"] = el.RegexSource ?? WireElementType(el.Type),
                ["formatter"] = el.Formatter,
            });
        }
        return arr;
    }

    private static string WireTarget(MailFilterTarget t) => t switch
    {
        MailFilterTarget.From => "from",
        MailFilterTarget.Body => "body",
        _ => "subject",
    };

    private static string WireComparator(MailFilterComparator c) => c switch
    {
        MailFilterComparator.Excludes => "excludes",
        MailFilterComparator.Matches => "matches",
        _ => "includes",
    };

    private static string WireElementType(MailElementType t) => t switch
    {
        MailElementType.Html => "html",
        MailElementType.Link => "link",
        MailElementType.Numeric => "numeric",
        _ => "text",
    };

    private static string SanitizeGroup(string value)
    {
        var clean = Regex.Replace(value.Trim(), @"[^A-Za-z0-9_-]", "_");
        return string.IsNullOrEmpty(clean) ? "default" : clean;
    }

    private static RequestOptions Options(string apiKey)
    {
        var o = new RequestOptions
        {
            Timeout = TimeSpan.FromSeconds(30),
            FollowRedirects = false,
            Tag = "aycd-inbox",
        };
        o.Headers["Authorization"] = "Token " + apiKey;
        return o;
    }

    private static JToken? TryParse(string body)
    {
        try { return JToken.Parse(body); }
        catch (JsonException) { return null; }
    }
}

/// <summary>
/// Shared message filter and element extractor aligned with <c>WaitImapAsync</c> (<c>0x140f40490</c>):
/// since-date cutoff, required/optional filters across Subject/From/Body, unique-recipient fallback,
/// HTML/Link/Numeric/Text elements, and <see cref="VerificationCodeExtractor"/> fallback.
/// </summary>
public static class MailMessageMatcher
{
    private static readonly Regex DefaultNumericRegex = new(@"\d+", RegexOptions.Compiled);
    private static readonly Regex HrefRegex = new(@"href\s*=\s*[""']([^""']+)[""']", RegexOptions.Compiled | RegexOptions.IgnoreCase);

    public static IReadOnlyList<MailFilter> EffectiveFilters(MailCodeRequest request)
    {
        if (request.Filters.Count == 0 &&
            string.IsNullOrEmpty(request.SenderContains) &&
            string.IsNullOrEmpty(request.SubjectContains))
            return Array.Empty<MailFilter>();

        var list = new List<MailFilter>(request.Filters);
        if (!string.IsNullOrEmpty(request.SenderContains))
        {
            list.Add(new MailFilter
            {
                Target = MailFilterTarget.From,
                Comparator = MailFilterComparator.Includes,
                Value = request.SenderContains,
            });
        }
        if (!string.IsNullOrEmpty(request.SubjectContains))
        {
            list.Add(new MailFilter
            {
                Target = MailFilterTarget.Subject,
                Comparator = MailFilterComparator.Includes,
                Value = request.SubjectContains,
            });
        }
        return list;
    }

    public static MailCodeResult? EvaluateMessages(
        IReadOnlyList<MailMessageSnapshot> messages,
        MailCodeRequest request,
        string source = "imap")
    {
        var dated = request.Since is { } since
            ? messages.Where(m => m.Date >= since).ToList()
            : messages.ToList();
        if (dated.Count == 0) return null;

        var filters = EffectiveFilters(request);
        List<MailMessageSnapshot> candidates;
        if (filters.Count == 0)
        {
            candidates = dated;
        }
        else
        {
            candidates = dated.Where(m => MatchesFilters(m, filters)).ToList();
        }

        // Recipient filtering & fallback (0x140f436b0): if filtered set is empty and !AllowMultiple,
        // fall back to a unique message addressed to the requested recipient.
        if (request.Recipient is { Length: > 0 } to)
        {
            var recipientMatches = candidates
                .Where(m => m.To.Any(addr => addr.Contains(to, StringComparison.OrdinalIgnoreCase)))
                .ToList();
            if (recipientMatches.Count > 0)
            {
                candidates = recipientMatches;
            }
            else if (candidates.Count == 0 && !request.AllowMultiple)
            {
                var fallback = dated
                    .Where(m => m.To.Any(addr => addr.Contains(to, StringComparison.OrdinalIgnoreCase)))
                    .ToList();
                if (fallback.Count == 1)
                    candidates = fallback;
            }
            else if (candidates.Any(m => m.To.Count > 0))
            {
                candidates = recipientMatches;
            }
        }

        foreach (var msg in candidates.OrderByDescending(m => m.Date))
        {
            var extracted = ExtractResult(msg, request, source);
            if (extracted is not null)
                return extracted;
        }

        return null;
    }

    public static MailCodeResult? EvaluateMessage(MailMessageSnapshot msg, MailCodeRequest request, string source = "imap")
        => EvaluateMessages(new[] { msg }, request, source);

    private static bool MatchesFilters(MailMessageSnapshot msg, IReadOnlyList<MailFilter> filters)
    {
        var required = filters.Where(f => !f.Optional).ToList();
        var optional = filters.Where(f => f.Optional).ToList();

        foreach (var f in required)
        {
            if (!MatchesSingleFilter(msg, f))
                return false;
        }

        if (required.Count == 0 && optional.Count > 0)
            return optional.Any(f => MatchesSingleFilter(msg, f));

        return true;
    }

    private static bool MatchesSingleFilter(MailMessageSnapshot msg, MailFilter filter)
    {
        var candidates = TargetTexts(msg, filter.Target, filter.RawHtml).ToList();
        if (candidates.Count == 0)
            return filter.Comparator == MailFilterComparator.Excludes;

        var values = new List<string>();
        if (!string.IsNullOrEmpty(filter.Value)) values.Add(filter.Value!);
        if (filter.OrValues is not null) values.AddRange(filter.OrValues.Where(v => !string.IsNullOrEmpty(v)));
        if (values.Count == 0) return true;

        bool hit = filter.Comparator switch
        {
            MailFilterComparator.Matches => candidates.Any(t => values.Any(p => Regex.IsMatch(t, p, RegexOptions.IgnoreCase))),
            _ => candidates.Any(t => values.Any(v => t.Contains(v, StringComparison.OrdinalIgnoreCase))),
        };

        return filter.Comparator == MailFilterComparator.Excludes ? !hit : hit;
    }

    private static IEnumerable<string> TargetTexts(MailMessageSnapshot msg, MailFilterTarget target, bool rawHtml)
    {
        switch (target)
        {
            case MailFilterTarget.Subject:
                if (!string.IsNullOrEmpty(msg.Subject)) yield return msg.Subject!;
                yield break;
            case MailFilterTarget.From:
                foreach (var f in msg.From)
                    if (!string.IsNullOrEmpty(f)) yield return f;
                yield break;
            case MailFilterTarget.Body:
            default:
                var body = rawHtml
                    ? (msg.HtmlBody ?? msg.TextBody)
                    : (msg.TextBody ?? (msg.HtmlBody is null ? null : VerificationCodeExtractor.StripHtmlPublic(msg.HtmlBody)));
                if (!string.IsNullOrEmpty(body)) yield return body!;
                yield break;
        }
    }

    private static MailCodeResult? ExtractResult(MailMessageSnapshot msg, MailCodeRequest request, string source)
    {
        if (request.Elements.Count == 0)
        {
            var combined = (msg.Subject ?? string.Empty) + "\n" + (msg.TextBody ?? msg.HtmlBody ?? string.Empty);
            var code = VerificationCodeExtractor.Extract(combined);
            if (code is null) return null;

            return new MailCodeResult
            {
                Ok = true,
                Code = code,
                Subject = msg.Subject,
                From = msg.From.FirstOrDefault(),
                Received = msg.Date,
                Source = source,
                Values = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase) { ["code"] = code },
            };
        }

        var values = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        foreach (var el in request.Elements)
        {
            var raw = ExtractElementValue(msg, el);
            if (string.IsNullOrEmpty(raw))
            {
                if (!el.Optional) return null;
                continue;
            }
            values[el.Name] = raw!;
        }

        var primary = values.TryGetValue("code", out var explicitCode)
            ? explicitCode
            : values.Values.FirstOrDefault();
        if (string.IsNullOrEmpty(primary)) return null;

        return new MailCodeResult
        {
            Ok = true,
            Code = primary,
            Subject = msg.Subject,
            From = msg.From.FirstOrDefault(),
            Received = msg.Date,
            Source = source,
            Values = values,
        };
    }

    private static string? ExtractElementValue(MailMessageSnapshot msg, MailElement el)
    {
        var sourceText = string.Join("\n", TargetTexts(msg, el.Target, el.RawHtml || el.Type is MailElementType.Html or MailElementType.Link));
        if (string.IsNullOrEmpty(sourceText)) return null;

        var candidate = sourceText;
        if (!string.IsNullOrEmpty(el.Formatter))
        {
            var idx = candidate.IndexOf(el.Formatter, StringComparison.OrdinalIgnoreCase);
            if (idx >= 0)
                candidate = candidate[(idx + el.Formatter!.Length)..].TrimStart();
        }

        if (el.Type == MailElementType.Link)
        {
            if (!string.IsNullOrEmpty(el.Selector) && !el.Selector.StartsWith('/') && !el.Selector.StartsWith('('))
            {
                var hrefMatch = HrefRegex.Matches(msg.HtmlBody ?? candidate)
                    .Select(m => m.Groups[1].Value)
                    .FirstOrDefault(u => string.IsNullOrEmpty(el.Regex) || Regex.IsMatch(u, el.Regex, RegexOptions.IgnoreCase));
                if (!string.IsNullOrEmpty(hrefMatch))
                    return hrefMatch;
            }
        }

        if (!string.IsNullOrEmpty(el.Regex))
        {
            var m = Regex.Match(candidate, el.Regex, RegexOptions.IgnoreCase | RegexOptions.Singleline);
            if (!m.Success) return null;
            var value = m.Groups.Count <= 1 ? m.Value : m.Groups[1].Value;
            if (el.Type == MailElementType.Numeric)
            {
                var num = DefaultNumericRegex.Match(value);
                return num.Success ? (num.Groups.Count <= 1 ? num.Value : num.Groups[1].Value) : null;
            }
            return value;
        }

        if (el.Type == MailElementType.Numeric)
        {
            var m = DefaultNumericRegex.Match(candidate);
            if (!m.Success) return null;
            return m.Groups.Count <= 1 ? m.Value : m.Groups[1].Value;
        }

        return candidate.Trim();
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

        var cleaned = MoneyPattern.Replace(stripped, " ");
        cleaned = OrderPattern.Replace(cleaned, " ");

        var candidates = new List<(string Code, int Score)>();
        foreach (Match m in CodePattern.Matches(cleaned))
        {
            var code = m.Groups[1].Value;
            var score = 0;

            if (strongHit) score += 4;
            else if (weakHit) score += 1;

            var window = WindowAround(cleaned, m.Index, 60).ToLowerInvariant();
            if (StrongKeywords.Any(k => window.Contains(k, StringComparison.Ordinal))) score += 5;
            else if (WeakKeywords.Any(k => window.Contains(k, StringComparison.Ordinal))) score += 2;

            score += code.Length switch { 6 => 3, 5 or 7 => 2, 4 => 1, _ => 0 };

            var numeric = int.Parse(code);
            if (code.Length == 4 && numeric is >= 1900 and <= 2100) score -= 6;
            if (code.Length >= 7 && code.StartsWith("000")) score -= 3;

            candidates.Add((code, score));
        }

        var best = candidates.OrderByDescending(c => c.Score).FirstOrDefault();
        return best.Score > 0 ? best.Code : null;
    }

    internal static string StripHtmlPublic(string html) => StripHtml(html);

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
