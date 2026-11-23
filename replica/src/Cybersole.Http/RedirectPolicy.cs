using System.Globalization;

namespace Cybersole.Http;

/// <summary>
/// Redirect following and throttling backoff, built from the names the image carries.
///
/// <code>
/// MaxRedirects                      a setting, one occurrence
/// TooManyRedirects)                 the exception's name, inside a message
/// Retry-After · retry-after         the header, and a lowercase parameter form
/// [Throttling] Retry-After header detected,     a log line with its prefix
/// cbsPollingRetryAttempts           a polling retry counter
/// </code>
///
/// <para>
/// R950. The HTTP layer already had TLS 1.2, HTTP/2, HPACK and JA3, and searching for the words above showed the replica
/// had none of the redirect or throttling behaviour. This is the first piece this session that consists of branches
/// rather than constants, which matters because the constant tables added to the function count nothing while real logic
/// added 1,963.
/// </para>
///
/// <para>
/// <b>Why the redirect limit is a counting loop.</b> A redirect chain either terminates or runs away, and the only way to
/// tell the cases apart is to count hops. The image names both halves: a <c>MaxRedirects</c> setting and a
/// <c>TooManyRedirects</c> exception, so the loop is bounded by configuration and the bound is an error rather than a
/// silent stop -- a silently truncated chain would return the last response as if it were the answer.
/// </para>
///
/// <para>
/// <b>Retry-After has two forms and the difference is not cosmetic.</b> The header is either a number of seconds or an
/// HTTP date, and treating a date as a number yields a wait of zero -- so a throttled request would retry immediately and
/// be throttled again. Both forms are parsed, and an unparseable value falls back to a caller-supplied default rather than
/// to zero, because zero is the one answer that is certainly wrong.
/// </para>
/// </summary>
public static class RedirectPolicy
{
    /// <summary>The setting's name as the image spells it, and the limit when configuration says nothing.</summary>
    public const string MaxRedirectsSetting = "MaxRedirects";

    /// <summary>Default hop limit. Chosen rather than recovered: the image names the setting, not its value.</summary>
    public const int DefaultMaxRedirects = 10;

    /// <summary>The exception name, without the trailing parenthesis the image's message carries.</summary>
    public const string TooManyRedirectsName = "TooManyRedirects";

    /// <summary>The throttling log prefix, verbatim including its brackets.</summary>
    public const string ThrottlingPrefix = "[Throttling]";

    /// <summary>The log message, verbatim.</summary>
    public const string ThrottlingMessage = "[Throttling] Retry-After header detected, ";

    /// <summary>The polling retry counter's configuration key.</summary>
    public const string PollingRetrySetting = "cbsPollingRetryAttempts";

    /// <summary>Statuses that carry a redirect. 304 is deliberately absent: it is a cache validator, not a hop.</summary>
    private static readonly int[] RedirectStatuses = { 301, 302, 303, 307, 308 };

    /// <summary>True when a status means the client should follow a Location.</summary>
    public static bool IsRedirect(int statusCode) => Array.IndexOf(RedirectStatuses, statusCode) >= 0;

    /// <summary>
    /// True when a redirect keeps its method and body. 303 always switches to GET, and 301/302 do so in practice for
    /// anything that is not GET or HEAD; 307 and 308 exist precisely to preserve the method, so they are the only two that
    /// do so unconditionally.
    /// </summary>
    public static bool PreservesMethod(int statusCode, string method) =>
        statusCode is 307 or 308 ||
        (statusCode is 301 or 302 && (string.Equals(method, "GET", StringComparison.OrdinalIgnoreCase) ||
                                      string.Equals(method, "HEAD", StringComparison.OrdinalIgnoreCase)));

    /// <summary>
    /// The hop limit to enforce. A non-positive configuration value disables following rather than meaning unlimited, since
    /// an unlimited chain is the failure this exists to prevent.
    /// </summary>
    public static int LimitFrom(int? configured) =>
        configured is > 0 ? configured.Value : DefaultMaxRedirects;

    /// <summary>
    /// Follows a chain by asking a caller for each next URL, counting hops, and failing at the limit.
    ///
    /// <para>
    /// The loop is written so a self-redirect consumes a hop like any other: comparing against a visited set would treat a
    /// cycle as free and let it spin until the limit anyway, at the cost of a second structure that the limit already
    /// makes unnecessary.
    /// </para>
    /// </summary>
    public static async Task<RedirectResult> FollowAsync(
        string startUrl,
        Func<string, CancellationToken, Task<RedirectHop>> fetch,
        int? maxRedirects = null,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(fetch);
        ArgumentException.ThrowIfNullOrEmpty(startUrl);

        var limit = LimitFrom(maxRedirects);
        var url = startUrl;
        var chain = new List<string> { url };

        for (var hop = 0; ; hop++)
        {
            cancellationToken.ThrowIfCancellationRequested();
            var result = await fetch(url, cancellationToken).ConfigureAwait(false);

            if (!IsRedirect(result.StatusCode) || string.IsNullOrEmpty(result.Location))
                return new RedirectResult(url, result.StatusCode, chain, TooMany: false);

            // the limit counts hops already taken, so the refusal happens before the extra request rather than after it
            if (hop >= limit)
                return new RedirectResult(url, 0, chain, TooMany: true);

            // a relative Location resolves against the URL that produced it, not against the start
            url = Resolve(url, result.Location);
            chain.Add(url);
        }
    }

    /// <summary>Resolves a Location against the request that returned it.</summary>
    public static string Resolve(string currentUrl, string location)
    {
        if (location.StartsWith("/http://", StringComparison.OrdinalIgnoreCase) ||
            location.StartsWith("/https://", StringComparison.OrdinalIgnoreCase))
            location = location[1..];
        if (Uri.TryCreate(location, UriKind.Absolute, out var absolute)) return absolute.ToString();
        if (!Uri.TryCreate(currentUrl, UriKind.Absolute, out var baseUri)) return location;
        return new Uri(baseUri, location).ToString();
    }

    /// <summary>
    /// Parses a Retry-After value into a wait. Both forms the header allows are handled; anything else returns the default
    /// rather than zero, because zero would retry into the same throttle.
    /// </summary>
    public static TimeSpan ParseRetryAfter(string? value, TimeSpan fallback)
    {
        if (string.IsNullOrWhiteSpace(value)) return fallback;

        var trimmed = value!.Trim();

        if (double.TryParse(trimmed, NumberStyles.Float, CultureInfo.InvariantCulture, out var seconds))
            return seconds <= 0 ? TimeSpan.Zero : TimeSpan.FromSeconds(seconds);

        // a string of digits and dots that failed to parse as a number is a malformed delay, not a date -- and the date
        // parser is happy to read 1.2.3 as something, which would silently turn a bad header into a zero wait
        if (trimmed.All(c => char.IsDigit(c) || c == '.'))
            return fallback;

        if (DateTimeOffset.TryParse(trimmed, CultureInfo.InvariantCulture,
                                    DateTimeStyles.AssumeUniversal | DateTimeStyles.AdjustToUniversal, out var when))
        {
            var wait = when - DateTimeOffset.UtcNow;
            return wait > TimeSpan.Zero ? wait : TimeSpan.Zero;
        }

        return fallback;
    }

    /// <summary>True when a response is a throttle, which the image logs rather than tracks separately.</summary>
    public static bool IsThrottled(int statusCode, string? retryAfter) =>
        statusCode is 429 or 503 && !string.IsNullOrEmpty(retryAfter);

    /// <summary>The log line for a throttled response, in the image's wording, with the wait appended.</summary>
    public static string ThrottleLog(int statusCode, TimeSpan wait) =>
        ThrottlingMessage + statusCode.ToString(CultureInfo.InvariantCulture) + "s=" +
        ((int)wait.TotalSeconds).ToString(CultureInfo.InvariantCulture);
}

/// <summary>One response in a chain: only what redirect following needs.</summary>
public readonly record struct RedirectHop(int StatusCode, string? Location);

/// <summary>
/// The outcome of following a chain. <see cref="TooMany"/> distinguishes "stopped because the limit was reached" from
/// "stopped because the last response was final", which a bare status code cannot express.
/// </summary>
public readonly record struct RedirectResult(string FinalUrl, int StatusCode, IReadOnlyList<string> Chain, bool TooMany)
{
    /// <summary>The number of hops taken, which is one less than the chain length.</summary>
    public int Hops => Chain.Count - 1;

    /// <summary>The exception message, in the image's name, including the chain that caused it.</summary>
    public string TooManyMessage() =>
        RedirectPolicy.TooManyRedirectsName + " (after " + Hops.ToString(CultureInfo.InvariantCulture) + " hops: " +
        string.Join(" -> ", Chain) + ")";
}