"""R1379: the browser-side PayPal surface is in the image after all — one function names every header.

I had filed this as "needs a capture". It does not: sub_140F4C550 carries thirty-eight literals and they are the whole
surface —

    x-app-name            checkoutuinodeweb_hermione
    x-paypal-internal-euat
    paypal-client-metadata-id
    accept / content-type / cookie / origin / referer / user-agent
    sec-ch-ua / sec-ch-ua-mobile / sec-ch-ua-platform / sec-fetch-dest / sec-fetch-mode / sec-fetch-site
    accept-language = en-GB
    PayWithQuery, operationName, query, variables, token, withSplitTender, expeirences
    https://www.paypal.com, https://www.paypal.com/mep/dashboard, application/json, IFRAME, login, signin

So the browser path sends the same PayWithQuery operation with a PayPal-internal app name and two session headers the
page holds. The values of those two are per-session — the euat and the client metadata id — so they come from the
caller, exactly like the storefront token.

Usage: python analysis/add_paypal_browser_surface.py
"""
import io

MODEL = 'replica/src/Cybersole.Stores/Payments/PayPalBrowserSurface.cs'
TESTS = 'replica/tests/Cybersole.Tests/PayPalBrowserSurfaceTests.cs'

model = '''using System.Collections.Generic;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// The browser-side PayPal call path.
///
/// <para>
/// <b>Observed</b> (R1379): <c>sub_140F4C550</c> names every header this path sets — <c>x-app-name</c> with the value
/// <c>checkoutuinodeweb_hermione</c>, <c>x-paypal-internal-euat</c>, <c>paypal-client-metadata-id</c>, and the browser
/// set (<c>accept</c>, <c>content-type</c>, <c>cookie</c>, <c>origin</c>, <c>referer</c>, <c>user-agent</c>,
/// <c>sec-ch-ua</c>, <c>sec-ch-ua-mobile</c>, <c>sec-ch-ua-platform</c>, <c>sec-fetch-dest</c>,
/// <c>sec-fetch-mode</c>, <c>sec-fetch-site</c>, <c>accept-language</c> = <c>en-GB</c>) — and the body it sends is
/// <c>PayWithQuery</c> with <c>token</c>, <c>withSplitTender</c> and the field the image spells
/// <c>expeirences</c>.
/// </para>
///
/// <para>
/// <b>Not observed anywhere:</b> the two session values. The euat and the client metadata id belong to a page session,
/// so they are the caller's — the same rule the storefront access token follows.
/// </para>
/// </summary>
public static class PayPalBrowserSurface
{
    /// <summary>The origin the path talks to.</summary>
    public const string Origin = "https://www.paypal.com";

    /// <summary>The dashboard url the sender also names.</summary>
    public const string DashboardUrl = "https://www.paypal.com/mep/dashboard";

    /// <summary>The app name the browser path identifies itself with.</summary>
    public const string AppName = "checkoutuinodeweb_hermione";

    /// <summary>The operation the body carries.</summary>
    public const string OperationName = "PayWithQuery";

    /// <summary>The image's own spelling of the experiences field.</summary>
    public const string ExperiencesFieldName = "expeirences";

    /// <summary>The funding method the sender names beside the request.</summary>
    public const string FundingMethodIframe = "IFRAME";

    /// <summary>The language the sender asks for.</summary>
    public const string AcceptLanguage = "en-GB";

    /// <summary>Header names in the order the function names them.</summary>
    public static readonly string[] HeaderNames =
    {
        "accept", "content-type", "cookie", "origin", "referer", "user-agent",
        "x-app-name", "x-paypal-internal-euat", "paypal-client-metadata-id",
        "sec-ch-ua", "sec-ch-ua-mobile", "sec-ch-ua-platform",
        "sec-fetch-dest", "sec-fetch-mode", "sec-fetch-site", "accept-language",
    };

    /// <summary>
    /// The headers this path sets. The session's own values come from the caller; the constants above are the
    /// image's.
    /// </summary>
    public static JObject Headers(string? euat, string? clientMetadataId, string? cookie, string? userAgent,
        string? origin, string? referer, string? secChUa, string? secChUaMobile, string? secChUaPlatform)
    {
        var headers = new JObject
        {
            ["accept"] = "application/json",
            ["content-type"] = "application/json",
            ["x-app-name"] = AppName,
            ["accept-language"] = AcceptLanguage,
        };

        if (!string.IsNullOrEmpty(euat)) headers["x-paypal-internal-euat"] = euat;
        if (!string.IsNullOrEmpty(clientMetadataId)) headers["paypal-client-metadata-id"] = clientMetadataId;
        if (!string.IsNullOrEmpty(cookie)) headers["cookie"] = cookie;
        if (!string.IsNullOrEmpty(userAgent)) headers["user-agent"] = userAgent;
        headers["origin"] = origin ?? Origin;
        if (!string.IsNullOrEmpty(referer)) headers["referer"] = referer;
        if (!string.IsNullOrEmpty(secChUa)) headers["sec-ch-ua"] = secChUa;
        if (!string.IsNullOrEmpty(secChUaMobile)) headers["sec-ch-ua-mobile"] = secChUaMobile;
        if (!string.IsNullOrEmpty(secChUaPlatform)) headers["sec-ch-ua-platform"] = secChUaPlatform;
        headers["sec-fetch-dest"] = "empty";
        headers["sec-fetch-mode"] = "cors";
        headers["sec-fetch-site"] = "same-origin";
        return headers;
    }

    /// <summary>The request body: the operation, its document, and the three variables the image names.</summary>
    public static JObject Body(string document, string? token, bool withSplitTender, JObject? experiences = null)
    {
        var variables = new JObject
        {
            ["token"] = token,
            ["withSplitTender"] = withSplitTender,
            [ExperiencesFieldName] = experiences ?? new JObject(),
        };

        return new JObject
        {
            ["operationName"] = OperationName,
            ["query"] = document,
            ["variables"] = variables,
        };
    }

    /// <summary>A session that cannot supply the euat or the metadata id cannot use this path.</summary>
    public static (bool Usable, string Reason) CanSend(string? euat, string? clientMetadataId)
    {
        if (string.IsNullOrWhiteSpace(euat)) return (false, "browser surface: no x-paypal-internal-euat");
        if (string.IsNullOrWhiteSpace(clientMetadataId))
            return (false, "browser surface: no paypal-client-metadata-id");
        return (true, string.Empty);
    }
}
'''

io.open(MODEL, 'w', encoding='utf-8', newline='').write(model)
print('wrote %s' % MODEL)

tests = '''using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1379: the browser-side PayPal path. The header names, the app name and the body's three variables are the image's;
/// the two session values are the caller's.
/// </summary>
public sealed class PayPalBrowserSurfaceTests
{
    [Fact]
    public void TheSurfaceConstantsAreTheObservedOnes()
    {
        Assert.Equal("https://www.paypal.com", PayPalBrowserSurface.Origin);
        Assert.Equal("checkoutuinodeweb_hermione", PayPalBrowserSurface.AppName);
        Assert.Equal("PayWithQuery", PayPalBrowserSurface.OperationName);
        Assert.Equal("expeirences", PayPalBrowserSurface.ExperiencesFieldName);
        Assert.Equal("IFRAME", PayPalBrowserSurface.FundingMethodIframe);
        Assert.Equal("en-GB", PayPalBrowserSurface.AcceptLanguage);
        Assert.Equal(16, PayPalBrowserSurface.HeaderNames.Length);
    }

    [Fact]
    public void TheHeadersCarryTheAppNameAndTheSessionsValues()
    {
        var headers = PayPalBrowserSurface.Headers("euat-1", "meta-1", null, null, null, null, null, null, null);

        Assert.Equal("checkoutuinodeweb_hermione", headers["x-app-name"]!.ToObject<string>());
        Assert.Equal("euat-1", headers["x-paypal-internal-euat"]!.ToObject<string>());
        Assert.Equal("meta-1", headers["paypal-client-metadata-id"]!.ToObject<string>());
        Assert.Equal("https://www.paypal.com", headers["origin"]!.ToObject<string>());
        Assert.Equal("same-origin", headers["sec-fetch-site"]!.ToObject<string>());
        Assert.Null(headers["cookie"]);
    }

    /// <summary>Without the session values the path cannot be used, and it says which one is missing.</summary>
    [Fact]
    public void TheSessionValuesAreRequired()
    {
        Assert.False(PayPalBrowserSurface.CanSend(null, "meta").Usable);
        Assert.False(PayPalBrowserSurface.CanSend("euat", null).Usable);
        Assert.True(PayPalBrowserSurface.CanSend("euat", "meta").Usable);
    }

    [Fact]
    public void TheBodyKeepsTheImagesSpelling()
    {
        var body = PayPalBrowserSurface.Body("query PayWithQuery { }", "tok", true);

        Assert.Equal("PayWithQuery", body["operationName"]!.ToObject<string>());
        Assert.True(body["variables"]!["withSplitTender"]!.ToObject<bool>());
        Assert.NotNull(body["variables"]!["expeirences"]);
        Assert.Null(body["variables"]!["experiences"]);
    }
}
'''

io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('wrote %s' % TESTS)
