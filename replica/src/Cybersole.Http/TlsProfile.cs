using System.Net.Security;
using System.Security.Authentication;

namespace Cybersole.Http;

/// <summary>TLS / HTTP2 fingerprint description (Cybersole.Http.TlsClientOptions).</summary>
public sealed class TlsProfile
{
    public string Name { get; init; } = "chrome";
    /// <summary>JA3 string (version,ciphers,extensions,curves,point-formats).</summary>
    public string Ja3 { get; init; } = string.Empty;
    public string Ja3Hash { get; init; } = string.Empty;
    public List<int> CipherSuites { get; init; } = new();
    public List<string> Alpn { get; init; } = new() { "h2", "http/1.1" };
    public List<int> Curves { get; init; } = new() { 29, 23, 24 };
    public bool Grease { get; init; } = true;
    public bool Ech { get; init; } = true;
    public bool BoringPadding { get; init; } = true;
    public string AcceptLanguage { get; init; } = "en-US,en;q=0.9";
    /// <summary>
    /// True only for H3-capable profiles (<c>chrome_144..chrome_152_PSK</c> in the original Go/quic-go transport,
    /// selected only by ASICS via <c>chrome_150</c>; default <c>chrome_131</c> leaves H3 off).
    /// </summary>
    public bool SupportsHttp3 { get; init; }

    /// <summary>IANA names of the TLS 1.2 suites this profile advertises.</summary>
    public List<string> CipherSuiteNames { get; init; } = new();

    public string UserAgent { get; init; } =
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36";

    public string SecChUa { get; init; } = "\"Chromium\";v=\"148\", \"Not?A_Brand\";v=\"24\", \"Google Chrome\";v=\"148\"";
    public string SecChUaMobile { get; init; } = "?0";
    public string SecChUaPlatform { get; init; } = "\"Windows\"";

    public static TlsProfile Chrome { get; } = new()
    {
        Name = "chrome",
        Ja3 = "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-17513,29-23-24,0",
        CipherSuiteNames = new()
        {
            "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
            "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
            "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
            "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
            "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
        },
    };

    public static TlsProfile Firefox { get; } = new()
    {
        Name = "firefox",
        Ja3 = "771,4865-4867-4866-49195-49199-52393-52392-49196-49200-49162-49161-49171-49172-51-57-47-53-10,0-23-65281-10-11-35-16-5-51-43-13-45-28-27-65037,29-23-24-25-256-257,0",
        CipherSuiteNames = new()
        {
            "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
            "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
            "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
            "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
            "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
        },
    };

    public static TlsProfile Safari { get; } = new()
    {
        Name = "safari",
        Ja3 = "771,4865-4866-4867-49196-49195-52393-49200-49199-52392-49188-49187-49162-49161-49192-49191-49172-49171-157-156-61-60-53-47,0-23-65281-10-11-35-16-5-13-18-51-45-43-27,29-23-24-25,0",
        CipherSuiteNames = new()
        {
            "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
            "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
            "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
        },
    };

    public static IReadOnlyList<TlsProfile> All { get; } = new[] { Chrome, Firefox, Safari };

    /// <summary>
    /// The H3-capable profile (<c>chrome_150</c>) used by ASICS in the original store HTTP stack (<c>0x140968840</c>).
    /// Kept outside <see cref="All"/> so SChannel/Bouncy TLS-over-TCP sweeps continue covering the 3 core profiles.
    /// </summary>
    public static TlsProfile Chrome150 { get; } = new()
    {
        Name = "chrome_150",
        Ja3 = Chrome.Ja3,
        CipherSuiteNames = Chrome.CipherSuiteNames.ToList(),
        SupportsHttp3 = true,
    };

    public static TlsProfile ByName(string? name) =>
        string.Equals(name, Chrome150.Name, StringComparison.OrdinalIgnoreCase)
            ? Chrome150
            : string.Equals(name, "chrome_131", StringComparison.OrdinalIgnoreCase)
                ? Chrome
                : All.FirstOrDefault(p => string.Equals(p.Name, name, StringComparison.OrdinalIgnoreCase)) ?? Chrome;

    /// <summary>
    /// Build a real <see cref="CipherSuitesPolicy"/> from <see cref="CipherSuiteNames"/>.
    /// SChannel only honours TLS 1.2 suites; unsupported entries throw, so we degrade to null
    /// (system default) instead of failing the request.
    /// </summary>
    public CipherSuitesPolicy? BuildCipherPolicy()
    {
        if (CipherSuiteNames.Count == 0) return null;
        try
        {
            var suites = new List<TlsCipherSuite>(CipherSuiteNames.Count);
            foreach (var name in CipherSuiteNames)
            {
                if (Enum.TryParse<TlsCipherSuite>(name, ignoreCase: true, out var suite))
                    suites.Add(suite);
            }
            if (suites.Count == 0) return null;
#pragma warning disable CA1416 // guarded: unsupported platforms throw and fall back to null
            return new CipherSuitesPolicy(suites);
#pragma warning restore CA1416
        }
        catch (Exception)
        {
            // Windows SChannel does not accept an explicit suite list; degrade to the
            // system default (CA1416 is suppressed because this path is guarded by try/catch).
            return null;
        }
    }

    /// <summary>Copy of this profile with a different ALPN offer (used by the HTTP/1.1 path).</summary>
    public TlsProfile WithAlpn(params string[] alpn) => new()
    {
        Name = Name, Ja3 = Ja3, Ja3Hash = Ja3Hash, CipherSuites = CipherSuites,
        CipherSuiteNames = CipherSuiteNames, Alpn = alpn.ToList(), Curves = Curves,
        Grease = Grease, Ech = Ech, BoringPadding = BoringPadding,
        AcceptLanguage = AcceptLanguage, SupportsHttp3 = SupportsHttp3, UserAgent = UserAgent,
        SecChUa = SecChUa, SecChUaMobile = SecChUaMobile, SecChUaPlatform = SecChUaPlatform,
    };

    public List<SslApplicationProtocol> BuildAlpn()
        => Alpn.Select(a => new SslApplicationProtocol(a)).ToList();
}

/// <summary>Per-request options carried through the pipeline.</summary>
public sealed class RequestOptions
{
    public string? Proxy { get; set; }
    public TlsProfile Profile { get; set; } = TlsProfile.Chrome;
    public Dictionary<string, string> Headers { get; } = new(StringComparer.OrdinalIgnoreCase);
    public Dictionary<string, string> Cookies { get; } = new(StringComparer.OrdinalIgnoreCase);
    /// <summary>Out-of-band per-request middleware flags (for example <c>Akamai = "1"</c>), never serialized onto HTTP wire headers.</summary>
    public Dictionary<string, string> Properties { get; } = new(StringComparer.OrdinalIgnoreCase);
    /// <summary>When true, <see cref="NetClient"/> skips pre-populating default browser fingerprint headers and sends only <see cref="Headers"/>.</summary>
    public bool OverrideHeaders { get; set; }
    public TimeSpan Timeout { get; set; } = TimeSpan.FromSeconds(30);
    public int Retries { get; set; } = 2;
    public string? Tag { get; set; }
    public bool FollowRedirects { get; set; } = true;
    /// <summary>
    /// Hop limit for a redirect chain. Null means the default in <see cref="RedirectPolicy"/>; a non-positive
    /// value means do not follow, since an unlimited chain is the failure the limit exists to prevent.
    /// </summary>
    public int? MaxRedirects { get; set; }
    public HttpContent? Content { get; set; }
    public Cybersole.Http.Content.IBody? Body { get; set; }

    public RequestOptions Clone()
    {
        var c = new RequestOptions
        {
            Proxy = Proxy,
            Profile = Profile,
            OverrideHeaders = OverrideHeaders,
            Timeout = Timeout,
            Retries = Retries,
            Tag = Tag,
            FollowRedirects = FollowRedirects,
            MaxRedirects = MaxRedirects,
            Content = Content,
            Body = Body,
        };
        foreach (var (k, v) in Headers) c.Headers[k] = v;
        foreach (var (k, v) in Cookies) c.Cookies[k] = v;
        foreach (var (k, v) in Properties) c.Properties[k] = v;
        return c;
    }
}

/// <summary>Normalized response returned to store modules.</summary>
public sealed class NetResponse
{
    public required int StatusCode { get; init; }
    public required string Body { get; init; }
    public required Uri Url { get; init; }
    public Dictionary<string, string> Headers { get; init; } = new(StringComparer.OrdinalIgnoreCase);
    public Dictionary<string, string> Cookies { get; init; } = new(StringComparer.OrdinalIgnoreCase);
    public TimeSpan Elapsed { get; init; }

    /// <summary>
    /// Bytes that came off the wire, when the transport can observe them. For a compressed
    /// response that is the compressed size; the system stack hands back a decoded string and
    /// so reports the decoded length instead. The two are not comparable.
    ///
    /// Use <see cref="BodyBytes"/> to compare transports. Comparing <c>Bytes</c> between
    /// SChannel and the hand-written TLS path is meaningless because the server may answer one
    /// with gzip and the other uncompressed — that gap was once mistaken for data loss
    /// (a 5.5x difference on two HTTP 200s). See TransportParityProbeTests.
    /// </summary>
    public long Bytes { get; init; }

    /// <summary>Size of the decoded body — the number to compare between transports.</summary>
    public long BodyBytes => Body.Length;

    public string Protocol { get; init; } = "h2";

    public bool IsSuccess => StatusCode is >= 200 and < 400;
    public bool IsRedirect => StatusCode is 301 or 302 or 303 or 307 or 308;
    public bool IsCaptcha => StatusCode == 403 || StatusCode == 429;
}

/// <summary>Thrown when a request cannot be completed after retries.</summary>
public sealed class NetException : Exception
{
    public int? StatusCode { get; }
    public NetException(string message, int? statusCode = null, Exception? inner = null)
        : base(message, inner) => StatusCode = statusCode;
}

/// <summary>Which stack <see cref="NetClient"/> uses to talk to the wire.</summary>
public enum TransportMode
{
    /// <summary>Windows SChannel via SocketsHttpHandler (stable default).</summary>
    SChannel = 0,

    /// <summary>BouncyCastle ClientHello + HTTP/2 frames (controlled fingerprint).</summary>
    BouncyH2 = 1,

    /// <summary>
    /// Hand-written TLS 1.2 stack (this repo's own ClientHello, records, EMS, AES-GCM) + HTTP/2.
    /// No SChannel, no BouncyCastle.
    /// </summary>
    OwnTls = 3,

    /// <summary>BouncyCastle ClientHello + HTTP/1.1 (hosts without h2).</summary>
    BouncyHttp11 = 2,
}
