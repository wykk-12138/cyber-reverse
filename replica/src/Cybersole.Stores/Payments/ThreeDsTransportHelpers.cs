using System.Net;
using System.Net.Http;
using System.Text;
using System.Text.RegularExpressions;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// Shared HTTP, Base64Url, JWT, and HTML form extraction helpers for 3-D Secure and
/// offsite payment state machines (<see cref="UnzerGateway"/>, <see cref="CardinalThreeDs"/>,
/// <see cref="CheckoutComGateway"/>, and Shopify offsite convenience-store completion).
/// </summary>
internal static class ThreeDsTransportHelpers
{
    internal static string Base64UrlEncode(string text)
    {
        var bytes = Encoding.UTF8.GetBytes(text);
        return Convert.ToBase64String(bytes)
            .TrimEnd('=')
            .Replace('+', '-')
            .Replace('/', '_');
    }

    internal static JObject? DecodeJwtPayload(string? jwt)
    {
        if (string.IsNullOrWhiteSpace(jwt)) return null;
        var parts = jwt.Split('.');
        if (parts.Length < 2) return null;

        try
        {
            var payload = parts[1].Replace('-', '+').Replace('_', '/');
            switch (payload.Length % 4)
            {
                case 2: payload += "=="; break;
                case 3: payload += "="; break;
            }
            var json = Encoding.UTF8.GetString(Convert.FromBase64String(payload));
            return JObject.Parse(json);
        }
        catch
        {
            return null;
        }
    }

    internal static void ApplyHeaders(RequestOptions options, IDictionary<string, string>? headers)
    {
        if (headers is null || headers.Count == 0) return;

        if (options.OverrideHeaders)
        {
            foreach (var kv in headers)
                options.Headers[kv.Key] = kv.Value;
            return;
        }

        string? ua = null, lang = null, chUa = null, chMobile = null, chPlatform = null;
        foreach (var kv in headers)
        {
            if (kv.Key.Equals("User-Agent", StringComparison.OrdinalIgnoreCase)) ua = kv.Value;
            else if (kv.Key.Equals("Accept-Language", StringComparison.OrdinalIgnoreCase)) lang = kv.Value;
            else if (kv.Key.Equals("sec-ch-ua", StringComparison.OrdinalIgnoreCase)) chUa = kv.Value;
            else if (kv.Key.Equals("sec-ch-ua-mobile", StringComparison.OrdinalIgnoreCase)) chMobile = kv.Value;
            else if (kv.Key.Equals("sec-ch-ua-platform", StringComparison.OrdinalIgnoreCase)) chPlatform = kv.Value;
            else options.Headers[kv.Key] = kv.Value;
        }

        if (ua is not null || lang is not null || chUa is not null || chMobile is not null || chPlatform is not null)
        {
            var b = options.Profile;
            options.Profile = new TlsProfile
            {
                Name = b.Name,
                Ja3 = b.Ja3,
                Ja3Hash = b.Ja3Hash,
                CipherSuites = b.CipherSuites,
                Alpn = b.Alpn,
                Curves = b.Curves,
                Grease = b.Grease,
                Ech = b.Ech,
                BoringPadding = b.BoringPadding,
                AcceptLanguage = lang ?? b.AcceptLanguage,
                SupportsHttp3 = b.SupportsHttp3,
                CipherSuiteNames = b.CipherSuiteNames,
                UserAgent = ua ?? b.UserAgent,
                SecChUa = chUa ?? b.SecChUa,
                SecChUaMobile = chMobile ?? b.SecChUaMobile,
                SecChUaPlatform = chPlatform ?? b.SecChUaPlatform,
            };
        }
    }

    internal static void ApplyProperties(RequestOptions options, IDictionary<string, string>? properties)
    {
        if (properties is null || properties.Count == 0) return;
        foreach (var kv in properties)
            options.Properties[kv.Key] = kv.Value;
    }

    internal static async Task<NetResponse?> GetRawAsync(
        FlowContext c,
        string url,
        IDictionary<string, string>? headers,
        string tag,
        CancellationToken ct,
        bool followRedirects = true,
        TlsProfile? profile = null,
        bool overrideHeaders = false,
        IDictionary<string, string>? properties = null)
    {
        try
        {
            var options = c.Options(tag);
            options.FollowRedirects = followRedirects;
            options.OverrideHeaders = overrideHeaders;
            // R1303: the issuer hop re-fingerprints for its duration. The profile goes on before
            // ApplyHeaders, which preserves whatever the current profile carries (user agent, language,
            // client hints) while overriding the ones this call supplies.
            if (profile is not null) options.Profile = profile;
            ApplyProperties(options, properties);
            ApplyHeaders(options, headers);

            var res = await c.Http.GetAsync(url, options, ct).ConfigureAwait(false);
            c.Session.AbsorbCookies(res.Cookies);
            c.Session.Vars["lastStatus"] = res.StatusCode.ToString();
            c.Session.Vars["lastUrl"] = res.Url.ToString();
            return res;
        }
        catch (Exception ex)
        {
            c.Emit($"{tag}: {ex.Message}", "error");
            return null;
        }
    }

    internal static async Task<NetResponse?> PostJsonRawAsync(
        FlowContext c,
        string url,
        string json,
        IDictionary<string, string>? headers,
        string tag,
        CancellationToken ct,
        string contentType = "application/json",
        bool overrideHeaders = false,
        IDictionary<string, string>? properties = null)
    {
        try
        {
            var options = c.Options(tag);
            options.FollowRedirects = true;
            options.OverrideHeaders = overrideHeaders;
            ApplyProperties(options, properties);
            ApplyHeaders(options, headers);

            var content = new StringContent(json ?? string.Empty, Encoding.UTF8);
            if (System.Net.Http.Headers.MediaTypeHeaderValue.TryParse(contentType, out var parsedCt))
                content.Headers.ContentType = parsedCt;
            options.Content = content;
            var res = await c.Http.SendAsync(HttpMethod.Post, url, options, ct).ConfigureAwait(false);
            c.Session.AbsorbCookies(res.Cookies);
            c.Session.Vars["lastStatus"] = res.StatusCode.ToString();
            c.Session.Vars["lastUrl"] = res.Url.ToString();
            return res;
        }
        catch (Exception ex)
        {
            c.Emit($"{tag}: {ex.Message}", "error");
            return null;
        }
    }

    internal static async Task<NetResponse?> PostFormRawAsync(
        FlowContext c,
        string url,
        IDictionary<string, string> form,
        IDictionary<string, string>? headers,
        string tag,
        CancellationToken ct,
        Encoding? encoding = null,
        bool followRedirects = true,
        bool overrideHeaders = false,
        IDictionary<string, string>? properties = null)
    {
        try
        {
            var options = c.Options(tag);
            options.FollowRedirects = followRedirects;
            options.OverrideHeaders = overrideHeaders;
            ApplyProperties(options, properties);
            ApplyHeaders(options, headers);

            if (encoding is null || Equals(encoding, Encoding.UTF8))
            {
                options.Content = new FormUrlEncodedContent(form);
            }
            else
            {
                var encoded = string.Join("&", form.Select(kv =>
                    EncodeFormPart(kv.Key, encoding) + "=" + EncodeFormPart(kv.Value ?? string.Empty, encoding)));
                var content = new ByteArrayContent(encoding.GetBytes(encoded));
                content.Headers.ContentType =
                    new System.Net.Http.Headers.MediaTypeHeaderValue("application/x-www-form-urlencoded")
                    {
                        CharSet = encoding.WebName,
                    };
                options.Content = content;
            }

            var res = await c.Http.SendAsync(HttpMethod.Post, url, options, ct).ConfigureAwait(false);
            c.Session.AbsorbCookies(res.Cookies);
            c.Session.Vars["lastStatus"] = res.StatusCode.ToString();
            c.Session.Vars["lastUrl"] = res.Url.ToString();
            return res;
        }
        catch (Exception ex)
        {
            c.Emit($"{tag}: {ex.Message}", "error");
            return null;
        }
    }

    internal static string EncodeFormPart(string value, Encoding encoding)
    {
        var bytes = encoding.GetBytes(value ?? string.Empty);
        var sb = new StringBuilder(bytes.Length * 2);
        foreach (var b in bytes)
        {
            if ((b >= 'a' && b <= 'z') || (b >= 'A' && b <= 'Z') || (b >= '0' && b <= '9') ||
                b == '-' || b == '_' || b == '.' || b == '*')
            {
                sb.Append((char)b);
            }
            else if (b == ' ')
            {
                sb.Append('+');
            }
            else
            {
                sb.Append('%').Append(b.ToString("X2"));
            }
        }
        return sb.ToString();
    }

    internal static (string? Action, Dictionary<string, string> Inputs) ExtractForm(string? html, string? formName = null)
    {
        var form = HtmlFormDom.ExtractFormInfo(html, formName: formName);
        return form is null
            ? (null, new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase))
            : (form.Action, form.Inputs);
    }

    internal static string? ReadMetaContent(string? html, string metaName) =>
        HtmlFormDom.ExtractMetaContent(html, metaName);

    internal static string ResolveUrl(string baseUrl, string relativeOrAbsolute)
    {
        if (string.IsNullOrEmpty(relativeOrAbsolute)) return baseUrl;
        if (Uri.TryCreate(relativeOrAbsolute, UriKind.Absolute, out var abs)) return abs.ToString();
        if (Uri.TryCreate(baseUrl, UriKind.Absolute, out var baseUri) &&
            Uri.TryCreate(baseUri, relativeOrAbsolute, out var combined))
            return combined.ToString();
        return relativeOrAbsolute;
    }

    internal static string OriginOf(string url)
    {
        var u = new Uri(url);
        return u.GetLeftPart(UriPartial.Authority);
    }

    internal static JObject? TryParseJson(string? text)
    {
        if (string.IsNullOrWhiteSpace(text)) return null;
        try { return JObject.Parse(text); }
        catch { return null; }
    }
}
