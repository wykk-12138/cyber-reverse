using System.Globalization;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// Queue-it, read out of a class's own field list rather than guessed from a product name.
///
/// <code>
/// QueueHostMarkers        determines whether a page is a Queue-it surface at all
/// AcceptedCookiePrefix    QueueITAccepted-SDFrts345E-V3_
/// CookieValiditySeconds   how long a pass lasts
/// MinRemainingSeconds     how much must be left for a pass to count
/// </code>
///
/// <para>
/// R959. The image also carries the control-flow strings — "Fetching Queue-it challenge", "Initiliazing Queue-it",
/// "Error Solving Queue-it (Softblock)", "Queue-IT banned, rotating proxy" — and one of them is misspelled. Both are
/// recorded as they are, because a replica that corrects the spelling stops matching the original's own messages.
/// </para>
///
/// <para>
/// <b>Why MinRemainingSeconds exists and why it matters.</b> A pass whose remaining validity is nearly zero is worse than
/// no pass: the request it authorises will be refused part way through, after the queue has already been left. So the
/// check is not "is it valid" but "is it valid for long enough to finish", and the constant that answers the second
/// question is the one the image names.
/// </para>
/// </summary>
public static class QueueItProtocol
{
    /// <summary>The host marker the image matches on, with its leading dot.</summary>
    public const string HostSuffix = ".queue-it.net";

    /// <summary>The waiting-room path prefix, present once in the image.</summary>
    public const string WaitingRoomPrefix = "waitingroom.";

    /// <summary>
    /// The pass cookie's prefix, verbatim: the hash in it is part of the cookie's name and not a placeholder, so it is
    /// kept exactly rather than normalised.
    /// </summary>
    public const string AcceptedCookiePrefix = "QueueITAccepted-SDFrts345E-V3_";

    /// <summary>The image's own wording, including the misspelling, which is deliberate.</summary>
    internal static readonly string[] Messages =
    {
        "Fetching Queue-it challenge",
        "Initiliazing Queue-it",              // misspelled in the image
        "Error Initiliazing Queue-it (Softblock)",
        "Error Solving Queue-it (Softblock)",
        "Queue-IT banned, rotating proxy",
    };

    /// <summary>The handler names, in the three spellings the image contains.</summary>
    internal static readonly string[] HandlerNames = { "QueueItHandler", "queueItHandler", "_queueItHandler" };

    /// <summary>True when a host is a Queue-it surface.</summary>
    public static bool IsQueueHost(string? host) =>
        !string.IsNullOrEmpty(host) &&
        (host.EndsWith(HostSuffix, StringComparison.OrdinalIgnoreCase) ||
         host.StartsWith(WaitingRoomPrefix, StringComparison.OrdinalIgnoreCase));

    /// <summary>
    /// The pass cookie for a queue id, which is the prefix plus the id. Kept as a function so the prefix cannot be
    /// concatenated by hand into a name with a stray separator.
    /// </summary>
    public static string CookieName(string queueId) => AcceptedCookiePrefix + (queueId ?? string.Empty);

    /// <summary>True when a cookie name is a Queue-it pass, whatever queue it belongs to.</summary>
    public static bool IsAcceptedCookie(string? name) =>
        !string.IsNullOrEmpty(name) && name!.StartsWith(AcceptedCookiePrefix, StringComparison.Ordinal);

    /// <summary>
    /// Whether a pass is worth using. Two conditions, and the second is the one the image's field names insist on: a pass
    /// about to expire is worse than none, because the request it authorises fails after the queue has been left.
    /// </summary>
    public static bool IsUsable(DateTimeOffset expiresAt, DateTimeOffset now, TimeSpan minRemaining) =>
        expiresAt - now >= minRemaining;

    /// <summary>
    /// Decides what to do with a queue response: entering the queue, holding a pass, or being refused outright.
    /// </summary>
    public static QueueVerdict Verdict(int statusCode, bool hasAcceptedCookie, TimeSpan? retryAfter = null)
    {
        if (statusCode is 401 or 403) return QueueVerdict.Banned;
        if (statusCode is 429 or 503) return QueueVerdict.RetryLater;
        if (hasAcceptedCookie) return QueueVerdict.Passed;

        // a 200 without a pass is the waiting room itself: the page loads, the queue is not finished
        return statusCode is >= 200 and < 300 ? QueueVerdict.Waiting : QueueVerdict.Failed;
    }

    /// <summary>The log line for a verdict, using the image's wording where it has one.</summary>
    public static string Describe(QueueVerdict verdict) => verdict switch
    {
        QueueVerdict.Passed => "Queue-it passed",
        QueueVerdict.Waiting => Messages[0],
        QueueVerdict.Banned => Messages[4],
        QueueVerdict.RetryLater => "Queue-it rate limited, retrying",
        _ => Messages[3],
    };
}

/// <summary>What a queue response amounts to. Separate from the status code because two statuses can mean the same thing.</summary>
public enum QueueVerdict
{
    /// <summary>The waiting room is showing; nothing to do but wait.</summary>
    Waiting = 0,

    /// <summary>A usable pass is held.</summary>
    Passed = 1,

    /// <summary>Refused outright, which the image answers with a proxy rotation.</summary>
    Banned = 2,

    /// <summary>Rate limited or unavailable; worth trying again.</summary>
    RetryLater = 3,

    /// <summary>Something the shape above does not explain.</summary>
    Failed = 4,
}