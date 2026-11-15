using System;
using System.Collections.Generic;
using System.Globalization;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// Builds the session payload the image posts, in the sample's key order (R153).
///
/// <para>
/// <see cref="SessionPayload"/> recorded the schema from a captured sample; this turns it into something a
/// telemetry path can actually send. Three rules are carried over literally because they are what makes the
/// sample self-consistent:
/// </para>
///
/// <list type="number">
/// <item><c>cookie-_cc</c> is the first 24 characters of <c>_t</c> — the cookie is a truncation, not a second
/// value, so a reader that compares them always finds them agreeing.</item>
/// <item>The time quartet comes from one instant: <c>time-unix-epoch-ms</c>, <c>time-local</c>,
/// <c>time-string</c> and the four <c>time-tz-*</c> keys all describe the same moment, so the payload cannot
/// contradict itself about when it was built.</item>
/// <item><c>time-tz-fixed-locale-string</c> formats the <b>fixed</b> instant, not now. That is the whole point
/// of it: a fixed instant formatted in the host locale exposes a timezone claim that does not match the host.
/// </item>
/// </list>
///
/// <para>
/// The sample's value for it is <c>"6-3-2014, 07:58:39"</c>, which is the pattern <c>d-M-yyyy, HH:mm:ss</c> —
/// day without padding, month without padding, then a comma and a zero-padded clock. That pattern is used here
/// rather than a culture lookup, because the sample's culture is not one this machine is guaranteed to have
/// installed and the pattern itself is the evidence.
/// </para>
/// </summary>
public static class SessionPayloadBuilder
{
    /// <summary>The custom pattern the sample's <c>time-tz-fixed-locale-string</c> follows.</summary>
    public const string FixedLocalePattern = "d-M-yyyy, HH:mm:ss";

    /// <summary>Everything the payload needs, so the builder itself reads no clock and no environment.</summary>
    public sealed record Inputs
    {
        public required string Sid { get; init; }
        public required string Tid { get; init; }
        public required string Token { get; init; }
        public int CfFlags { get; init; } = SessionPayload.CfFlagsSample;
        public bool FreshCookie { get; init; } = true;

        /// <summary>The instant the payload describes.</summary>
        public required DateTimeOffset Now { get; init; }

        /// <summary>JavaScript's <c>getTimezoneOffset()</c> for that instant: minutes behind UTC.</summary>
        public required int TimezoneOffsetMinutes { get; init; }

        public bool HasDst { get; init; }
        public bool DstActive { get; init; }
        public int StandardOffsetMinutes { get; init; }

        /// <summary>The host's own name for the zone, e.g. <c>Midden-Europese zomertijd</c>.</summary>
        public string TimeString { get; init; } = string.Empty;

        /// <summary>The fixed instant's formatting in the host locale; the builder supplies the default.</summary>
        public string? FixedLocaleString { get; init; }
    }

    /// <summary>The fixed instant formatted the way the sample does.</summary>
    public static string FormatFixedLocale(DateTime fixedDate) =>
        fixedDate.ToString(FixedLocalePattern, CultureInfo.InvariantCulture);

    /// <summary>
    /// Build the payload. Keys are added in <see cref="SessionPayload.HeadKeys"/> order and
    /// <c>cookie-_cc</c> is derived, never passed in.
    /// </summary>
    public static JObject Build(Inputs inputs)
    {
        var payload = new JObject
        {
            ["sid"] = inputs.Sid,
            ["tid"] = inputs.Tid,
            ["_t"] = inputs.Token,
            ["cf_flags"] = SessionPayload.CfFlags(inputs.CfFlags),
            ["fresh-cookie"] = inputs.FreshCookie ? "true" : "false",
            ["cookie-_cc"] = SessionPayload.CookieTagFor(inputs.Token),
            ["time-unix-epoch-ms"] = inputs.Now.ToUnixTimeMilliseconds(),
            // The sample's time-local is the host's clock, not UTC: 1778830875801 is 07:41:15 UTC and the
            // sample says 09:41:15, because the host reports getTimezoneOffset() == -120. So the local
            // string is formatted from the same instant shifted by the negated offset — the two keys must
            // agree or the payload contradicts itself about when it was built (R153).
            ["time-local"] = inputs.Now
                .ToOffset(TimeSpan.FromMinutes(-inputs.TimezoneOffsetMinutes))
                .ToString("d-M-yyyy, HH:mm:ss", CultureInfo.InvariantCulture),
            ["time-string"] = inputs.TimeString,
            ["time-tz-offset-minutes"] = inputs.TimezoneOffsetMinutes,
            ["time-tz-has-dst"] = inputs.HasDst ? "true" : "false",
            ["time-tz-dst-active"] = inputs.DstActive ? "true" : "false",
            ["time-tz-std-offset"] = inputs.StandardOffsetMinutes,
            ["time-tz-fixed-locale-string"] =
                inputs.FixedLocaleString ?? FormatFixedLocale(SessionPayload.FixedLocaleDate),
            ["dom-local-tag"] = SessionPayload.CookieTagFor(inputs.Token),
            ["dom-session-tag"] = SessionPayload.CookieTagFor(inputs.Token),
        };

        return payload;
    }

    /// <summary>The keys the built payload carries, in order — the contract a test can hold.</summary>
    public static IReadOnlyList<string> KeyOrder(JObject payload)
    {
        var keys = new List<string>();
        foreach (var property in payload.Properties()) keys.Add(property.Name);
        return keys;
    }
}
