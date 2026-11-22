using System.Collections.Generic;
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

    /// <summary>
    /// Send the browser path's request. The session values are applied as headers first, the way the hash family does
    /// it, and a session without them is refused before anything leaves.
    /// </summary>
    public static async System.Threading.Tasks.Task<(JObject? Data, string Error)> SendAsync(
        Cybersole.Stores.Flows.FlowContext c, string document, string? token, bool withSplitTender,
        string? euat, string? clientMetadataId, string? cookie,
        System.Threading.CancellationToken ct)
    {
        var (usable, reason) = CanSend(euat, clientMetadataId);
        if (!usable) return (null, reason);

        c.Session.Headers["x-app-name"] = AppName;
        c.Session.Headers["x-paypal-internal-euat"] = euat!;
        c.Session.Headers["paypal-client-metadata-id"] = clientMetadataId!;
        c.Session.Headers["accept-language"] = AcceptLanguage;
        if (!string.IsNullOrEmpty(cookie)) c.Session.Headers["cookie"] = cookie!;

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, Origin + "/graphql", Body(document, token, withSplitTender), "paypal-browser", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "browser surface: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "browser surface: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var data = reply["data"] as JObject ?? reply;
            return (data, string.Empty);
        }
        catch (System.Exception ex)
        {
            return (null, "browser surface: " + ex.GetType().Name);
        }
    }
}
