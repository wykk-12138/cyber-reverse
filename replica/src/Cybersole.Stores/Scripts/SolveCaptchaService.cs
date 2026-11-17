namespace Cybersole.Stores.Scripts;

/// <summary>
/// The captcha-solving service the image calls, recovered from its own two URLs.
///
/// <code>
/// https://api.solvecaptcha.com/in.php        submit
/// https://api.solvecaptcha.com/res.php?key=  poll
/// SolveCaptchaService · &lt;SubmitPat&gt;d__11 · &lt;SolveCaptcha&gt;d__12 · &lt;SubmitCaptcha&gt;d__13
/// </code>
///
/// <para>
/// R961. SolveCaptchaAsync in StoreFlow was one of thirty-six steps that returned Ok without doing anything, so a flow
/// that needed a captcha solved was told it had been. The image carries the two endpoints and three consecutive state
/// machines, which is enough to do the submission and the poll rather than report success.
/// </para>
///
/// <para>
/// <b>Why the poll's second parameter matters.</b> The classic two-endpoint captcha service answers the poll with
/// <c>CAPCHA_NOT_READY</c> until the task is finished, and that answer is not an error -- it is the normal path. Treating it
/// as one would fail every solve that took longer than a single poll, so it is classified separately and leads back into
/// the same wait.
/// </para>
///
/// <para>
/// <b>What the image does not give.</b> The parameter names, the response format, and the balance check. Only the two URLs
/// are literal, so the field names below are the service's documented ones marked as inference rather than recovered from
/// this binary.
/// </para>
/// </summary>
public static class SolveCaptchaService
{
    /// <summary>The submission endpoint, verbatim.</summary>
    public const string SubmitUrl = "https://api.solvecaptcha.com/in.php";

    /// <summary>The poll endpoint up to and including its key parameter, verbatim.</summary>
    public const string PollUrlPrefix = "https://api.solvecaptcha.com/res.php?key=";

    /// <summary>The service's name, which the image also uses as a type name.</summary>
    public const string ServiceName = "SolveCaptchaService";

    /// <summary>The in-progress answer, which is not an error.</summary>
    public const string NotReady = "CAPCHA_NOT_READY";

    /// <summary>The success prefix, which precedes the token.</summary>
    public const string OkPrefix = "OK|";

    /// <summary>Inference: the field names the service documents, not recovered from this image.</summary>
    internal static readonly string[] SubmitFields = { "key", "method", "googlekey", "pageurl", "json" };

    /// <summary>The poll URL for a task id.</summary>
    public static string PollUrl(string apiKey, string taskId) =>
        PollUrlPrefix + Uri.EscapeDataString(apiKey ?? string.Empty) +
        "&action=get&id=" + Uri.EscapeDataString(taskId ?? string.Empty);

    /// <summary>
    /// Reads the submission answer. The service answers either a bare id or <c>OK|id</c>, and both are accepted because
    /// the image's own URL carries no version that would settle which.
    /// </summary>
    public static string? TaskIdFrom(string? answer)
    {
        if (string.IsNullOrWhiteSpace(answer)) return null;

        var text = answer!.Trim();
        if (text.StartsWith(OkPrefix, StringComparison.Ordinal)) text = text[OkPrefix.Length..];
        // the service answers ERROR_WRONG_USER_KEY and friends, so the prefix is what matters, not the bare word
        if (text.StartsWith("ERROR", StringComparison.OrdinalIgnoreCase)) return null;
        if (text.Length == 0 || text.Contains('|')) return null;

        return text;
    }

    /// <summary>What a poll answer amounts to. Three outcomes, because "not ready" is neither success nor failure.</summary>
    public static CaptchaPoll Poll(string? answer)
    {
        if (string.IsNullOrWhiteSpace(answer)) return new CaptchaPoll(CaptchaPollKind.NotReady, null);

        var text = answer!.Trim();

        if (text.Equals(NotReady, StringComparison.OrdinalIgnoreCase))
            return new CaptchaPoll(CaptchaPollKind.NotReady, null);

        if (text.StartsWith(OkPrefix, StringComparison.Ordinal))
        {
            var token = text[OkPrefix.Length..].Trim();
            return token.Length > 0
                ? new CaptchaPoll(CaptchaPollKind.Solved, token)
                : new CaptchaPoll(CaptchaPollKind.Failed, null);
        }

        // anything else is the service refusing: a wrong key, an unsupported type, an unpaid balance
        return new CaptchaPoll(CaptchaPollKind.Failed, null);
    }

    /// <summary>
    /// Builds the submission form. Every value is escaped because a page URL contains its own ampersands and a raw
    /// concatenation would truncate the form at the first one.
    /// </summary>
    public static Dictionary<string, string> SubmitForm(string apiKey, string method, string siteKey, string pageUrl) =>
        new()
        {
            ["key"] = apiKey ?? string.Empty,
            ["method"] = method ?? string.Empty,
            ["googlekey"] = siteKey ?? string.Empty,
            ["pageurl"] = pageUrl ?? string.Empty,
            ["json"] = "0",
        };
}

/// <summary>What a poll answer means. <see cref="NotReady"/> is the normal path and not a failure.</summary>
public enum CaptchaPollKind
{
    /// <summary>Still working; the caller waits and asks again.</summary>
    NotReady = 0,

    /// <summary>Finished, with the token.</summary>
    Solved = 1,

    /// <summary>The service refused.</summary>
    Failed = 2,
}

/// <summary>One poll result. The token is null unless the kind is <see cref="CaptchaPollKind.Solved"/>.</summary>
public readonly record struct CaptchaPoll(CaptchaPollKind Kind, string? Token);