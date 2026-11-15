using System;
using Cybersole.Stores.Scripts;
using Newtonsoft.Json.Linq;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 153: the payload schema becomes a payload.
///
/// <para>
/// R152 recorded what the image sends; this builds it. The three self-consistency rules are pinned here
/// because they are what makes the sample readable: the cookie tag is the token's prefix, the time quartet
/// describes one instant, and the fixed-locale string is a <b>fixed</b> instant rather than now — which is
/// exactly what lets a reader compare a claimed timezone against the host.
/// </para>
/// </summary>
public sealed class SessionPayloadBuilderTests
{
    private readonly ITestOutputHelper _out;

    public SessionPayloadBuilderTests(ITestOutputHelper output) => _out = output;

    private static SessionPayloadBuilder.Inputs Sample() => new()
    {
        Sid = "9a10c34d-32fa-448a-9198-c61cce83a2d2",
        Tid = "3bd808ffef1b18c53173677cfd6a681da5e2",
        Token = "ASaMBHzL7WoRfLL6ekqt4MuLNpqk5pjkxXylexghsjlpjqOuGive8Zl6zR5",
        CfFlags = 1006579,
        FreshCookie = true,
        Now = DateTimeOffset.FromUnixTimeMilliseconds(1778830875801),
        TimezoneOffsetMinutes = -120,
        HasDst = true,
        DstActive = true,
        StandardOffsetMinutes = -120,
        TimeString = "Fri May 15 2026 09:41:15 GMT+0200 (Midden-Europese zomertijd)",
    };

    /// <summary>The built payload carries exactly the sixteen head keys, in the sample's order.</summary>
    [Fact]
    public void TheKeysAreTheSampleOrder()
    {
        var payload = SessionPayloadBuilder.Build(Sample());
        var keys = SessionPayloadBuilder.KeyOrder(payload);

        Assert.Equal(SessionPayload.HeadKeys, keys);
        _out.WriteLine(payload.ToString(Newtonsoft.Json.Formatting.None));
    }

    /// <summary>The cookie tag is derived, and three keys carry it.</summary>
    [Fact]
    public void TheCookieTagIsTheTokensPrefix()
    {
        var inputs = Sample();
        var payload = SessionPayloadBuilder.Build(inputs);

        var tag = (string)payload["cookie-_cc"]!;
        Assert.Equal(inputs.Token[..SessionPayload.CookieTagLength], tag);
        Assert.Equal(tag, (string)payload["dom-local-tag"]!);
        Assert.Equal(tag, (string)payload["dom-session-tag"]!);

        // derived means it cannot be passed in wrongly: the record has no field for it
        Assert.Null(typeof(SessionPayloadBuilder.Inputs).GetProperty("CookieTag"));
    }

    /// <summary>The time quartet describes one instant, and the fixed string is not now.</summary>
    [Fact]
    public void TheTimeFieldsDescribeOneInstant()
    {
        var inputs = Sample();
        var payload = SessionPayloadBuilder.Build(inputs);

        Assert.Equal(1778830875801L, (long)payload["time-unix-epoch-ms"]!);
        Assert.Equal("15-5-2026, 09:41:15", (string)payload["time-local"]!);
        Assert.Equal(-120, (int)payload["time-tz-offset-minutes"]!);

        // the fixed string is the 2014 instant, deliberately not the payload's own time
        Assert.Equal("6-3-2014, 07:58:39", (string)payload["time-tz-fixed-locale-string"]!);
        Assert.Equal(SessionPayload.FixedLocaleSample,
            (string)payload["time-tz-fixed-locale-string"]!);
        Assert.NotEqual((string)payload["time-local"]!,
            (string)payload["time-tz-fixed-locale-string"]!);
    }

    /// <summary>The booleans are the sample's string form, not JSON booleans.</summary>
    [Fact]
    public void TheFlagsAreStrings()
    {
        var payload = SessionPayloadBuilder.Build(Sample());

        Assert.Equal("true", (string)payload["fresh-cookie"]!);
        Assert.Equal("true", (string)payload["time-tz-has-dst"]!);
        Assert.Equal("true", (string)payload["time-tz-dst-active"]!);
        Assert.Equal("1006579", (string)payload["cf_flags"]!);

        // and a caller that turns them off gets "false", never a missing key
        var off = SessionPayloadBuilder.Build(Sample() with { FreshCookie = false, DstActive = false });
        Assert.Equal("false", (string)off["fresh-cookie"]!);
        Assert.Equal("false", (string)off["time-tz-dst-active"]!);
    }

    /// <summary>The fixed pattern reproduces the sample exactly.</summary>
    [Fact]
    public void TheFixedPatternReproducesTheSample()
    {
        var formatted = SessionPayloadBuilder.FormatFixedLocale(SessionPayload.FixedLocaleDate);

        Assert.Equal("6-3-2014, 07:58:39", formatted);
        Assert.Equal(SessionPayload.FixedLocaleSample, formatted);
        Assert.Equal("d-M-yyyy, HH:mm:ss", SessionPayloadBuilder.FixedLocalePattern);

        _out.WriteLine(formatted);
    }

    /// <summary>A caller may supply its own formatting, and it is used verbatim.</summary>
    [Fact]
    public void TheFixedStringCanBeSupplied()
    {
        var payload = SessionPayloadBuilder.Build(Sample() with
        {
            FixedLocaleString = "06.03.2014 07:58:39",
        });

        Assert.Equal("06.03.2014 07:58:39", (string)payload["time-tz-fixed-locale-string"]!);
    }

    /// <summary>The builder reads no clock: the same inputs give the same bytes twice.</summary>
    [Fact]
    public void TheBuilderIsDeterministic()
    {
        var a = SessionPayloadBuilder.Build(Sample()).ToString(Newtonsoft.Json.Formatting.None);
        var b = SessionPayloadBuilder.Build(Sample()).ToString(Newtonsoft.Json.Formatting.None);

        Assert.Equal(a, b);
        Assert.StartsWith("{\"sid\":", a, StringComparison.Ordinal);
        _out.WriteLine($"{a.Length} characters, stable across calls");
    }
}
