using System.Net.Security;
using System.Net.Sockets;
using System.Text;
using Org.BouncyCastle.Security;
using Org.BouncyCastle.Tls;
using Org.BouncyCastle.Tls.Crypto.Impl.BC;

namespace Cybersole.Http;

/// <summary>
/// BouncyCastle-backed TLS client used to build a *controlled* ClientHello
/// (cipher list, ALPN, SNI, TLS versions) instead of relying on SChannel.
/// Extensions are encoded by hand so the exact byte layout is under our control —
/// the step required to eventually match a full JA3 fingerprint.
/// </summary>
public sealed class ProfileTlsClient : DefaultTlsClient
{
    private readonly string _host;
    private readonly TlsProfile _profile;

    public ProfileTlsClient(string host, TlsProfile profile, bool validateCertificates = false)
        : base(new BcTlsCrypto(new SecureRandom()))
    {
        _host = host;
        _profile = profile;
        ValidateCertificates = validateCertificates;
    }

    /// <summary>RFC 8701 GREASE cipher value.</summary>
    private const int GreaseCipher = 0x0A0A;

    /// <summary>RFC 8701 GREASE extension type.</summary>
    private const int GreaseExtensionType = 0x1A1A;

    public bool ValidateCertificates { get; }

    public int SelectedCipherSuite { get; private set; }
    public ProtocolVersion? SelectedVersion { get; private set; }

    public override void NotifySelectedCipherSuite(int cipherSuite)
    {
        SelectedCipherSuite = cipherSuite;
        base.NotifySelectedCipherSuite(cipherSuite);
    }

    public TlsClientContext? Context { get; private set; }

    public override void Init(TlsClientContext context)
    {
        Context = context;
        base.Init(context);
    }

    protected override int[] GetSupportedCipherSuites()
    {
        var suites = new List<int>();
        foreach (var name in _profile.CipherSuiteNames)
        {
            if (TryMapCipherSuite(name, out var id)) suites.Add(id);
        }
        if (suites.Count == 0)
            suites.AddRange(new[]
            {
                CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
                CipherSuite.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
                CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,
                CipherSuite.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
            });
        if (_profile.Grease) suites.Insert(0, GreaseCipher);
        return suites.ToArray();
    }

    // R1292, third reading, and the one the file that decides it supports: NetClient.Transport defaults to
    // TransportMode.SChannel, which builds a SocketsHttpHandler — the same platform stack the image ships
    // (1432D5FE6 SocketsHttpHandler, 1433D4B8A SslStream, 1436F9152 Http2StreamWindowManager, 146EA88EC
    // SocketsHttpHandler.Http2Support). On that path TLS 1.3, GREASE and HTTP/2 all come from the platform, in the
    // replica as in the image, so there is no gap to close there.
    //
    // R1293 closes the question: NetClient's handler sets EnabledSslProtocols = Tls12 | Tls13, MaxAutomaticRedirections
    // = 10, CipherSuitesPolicy from the profile, ApplicationProtocols from the profile's ALPN, AutomaticDecompression =
    // All and UseCookies = true — six properties, each the platform's own name for the same thing the image uses, so the
    // default path already matches on TLS version, TLS policy, ALPN, redirect cap, decompression and cookies.
    //
    // This class is the OwnTls fallback. It is a hand-written stack that offers 1.2 only, reachable solely by opting in,
    // and its handshake bytes will never equal the platform's. R1291 read a BouncyCastle string beside a suite name and
    // concluded the image used this library for TLS; the suite names (146EB3A24 / 146EB3A6C) are SslStream's.
    protected override ProtocolVersion[] GetSupportedVersions()
        => new[] { ProtocolVersion.TLSv12 };

    public override IDictionary<int, byte[]> GetClientExtensions()
    {
        IDictionary<int, byte[]> source;
        try
        {
            source = base.GetClientExtensions() ?? new Dictionary<int, byte[]>();
        }
        catch (Exception)
        {
            // no live TlsClientContext (unit tests / offline probing)
            source = new Dictionary<int, byte[]>();
        }

        // ---- hand-encoded SNI (type 0) ----
        var hostBytes = Encoding.ASCII.GetBytes(_host);
        var listLen = 1 + 2 + hostBytes.Length;
        var sni = new byte[2 + listLen];
        sni[0] = (byte)(listLen >> 8);
        sni[1] = (byte)listLen;
        sni[2] = 0x00; // host_name
        sni[3] = (byte)(hostBytes.Length >> 8);
        sni[4] = (byte)hostBytes.Length;
        hostBytes.CopyTo(sni, 5);
        source[ExtensionType.server_name] = sni;

        // ---- hand-encoded ALPN (type 16) ----
        var alpnEntries = _profile.Alpn.Select(a => Encoding.ASCII.GetBytes(a)).ToArray();
        var alpnLen = alpnEntries.Sum(e => 1 + e.Length);
        var alpn = new byte[2 + alpnLen];
        alpn[0] = (byte)(alpnLen >> 8);
        alpn[1] = (byte)alpnLen;
        var offset = 2;
        foreach (var entry in alpnEntries)
        {
            alpn[offset++] = (byte)entry.Length;
            entry.CopyTo(alpn, offset);
            offset += entry.Length;
        }
        source[ExtensionType.application_layer_protocol_negotiation] = alpn;

        // ---- Chrome 148 extension order (JA3 component 2) ----
        int[] chromeOrder =
        {
            0x0000, // server_name
            0x0017, // extended_master_secret
            0xFF01, // renegotiation_info
            0x000A, // supported_groups
            0x000B, // ec_point_formats
            0x0023, // session_ticket
            0x0010, // ALPN
            0x0005, // status_request
            0x000D, // signature_algorithms
            0x0012, // signed_certificate_timestamp
            0x002B, // supported_versions
            0x002D, // psk_key_exchange_modes
            0x001B, // certificate_authorities
            0x0027, // compress_certificate
        };

        var ordered = new OrderedExtensions();
        if (_profile.Grease)
            ordered[GreaseExtensionType] = Array.Empty<byte>();

        foreach (var type in chromeOrder)
            if (source.TryGetValue(type, out var payload))
                ordered[type] = payload;

        // keep anything BouncyCastle added that we did not list
        foreach (var kv in source)
            if (!ordered.ContainsKey(kv.Key))
                ordered[kv.Key] = kv.Value;

        // SCT request: empty body = "please include SCTs"
        if (!ordered.ContainsKey(0x0012))
            ordered[0x0012] = Array.Empty<byte>();

        return ordered;
    }

    public override TlsAuthentication GetAuthentication()
        => new AcceptAllAuthentication(ValidateCertificates);

    private static bool TryMapCipherSuite(string name, out int suite)
    {
        suite = 0;
        var field = typeof(CipherSuite).GetField(name,
            System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static);
        if (field?.GetValue(null) is int value)
        {
            suite = value;
            return true;
        }
        return false;
    }

    /// <summary>Certificate handling: accept-all by default (fingerprint probing).</summary>
    private sealed class AcceptAllAuthentication : TlsAuthentication
    {
        private readonly bool _validate;

        public AcceptAllAuthentication(bool validate) => _validate = validate;

        public void NotifyServerCertificate(TlsServerCertificate serverCertificate)
        {
            if (!_validate) return;
            var chain = serverCertificate.Certificate;
            if (chain == null) throw new TlsFatalAlert(AlertDescription.bad_certificate);
            var leaf = chain.GetCertificateAt(0);
            if (leaf == null) throw new TlsFatalAlert(AlertDescription.bad_certificate);
        }

        public TlsCredentials GetClientCredentials(CertificateRequest certificateRequest) => null!;
    }
}

/// <summary>Result of a BouncyCastle handshake.</summary>
public sealed record BcTlsProbeResult(
    string Host,
    bool Ok,
    string Protocol,
    string CipherSuite,
    int HandshakeMs,
    string? Error);

/// <summary>Handshake driver for <see cref="ProfileTlsClient"/>.</summary>
public static class BouncyTls
{
    public static async Task<(TlsClientProtocol? Protocol, BcTlsProbeResult Result)> ConnectAsync(
        string host, int port, TlsProfile profile,
        Cybersole.Core.Models.Proxy? proxy = null,
        CancellationToken ct = default)
    {
        var sw = System.Diagnostics.Stopwatch.StartNew();
        try
        {
            Stream transport;
            if (proxy is null)
            {
                var tcp = new TcpClient();
                await tcp.ConnectAsync(host, port, ct).ConfigureAwait(false);
                transport = tcp.GetStream();
            }
            else
            {
                transport = await ProxyConnector.ConnectAsync(proxy, host, port, ct).ConfigureAwait(false);
            }

            var client = new ProfileTlsClient(host, profile);
            var protocol = new TlsClientProtocol(transport);
            await Task.Run(() => protocol.Connect(client), ct).ConfigureAwait(false);
            sw.Stop();

            return (protocol, new BcTlsProbeResult(
                host, true,
                client.Context?.ServerVersion?.ToString() ?? "-",
                CipherSuiteName(client.SelectedCipherSuite),
                (int)sw.ElapsedMilliseconds,
                null));
        }
        catch (Exception ex)
        {
            sw.Stop();
            return (null, new BcTlsProbeResult(host, false, "-", "-", (int)sw.ElapsedMilliseconds, ex.Message));
        }
    }

    private static string CipherSuiteName(int id) => id switch
    {
        0xC02B => "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
        0xC02F => "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
        0xC02C => "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
        0xC030 => "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
        0xCCA9 => "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
        0xCCA8 => "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
        0x1301 => "TLS_AES_128_GCM_SHA256",
        0x1302 => "TLS_AES_256_GCM_SHA384",
        0x1303 => "TLS_CHACHA20_POLY1305_SHA256",
        _ => $"0x{id:X4}",
    };
}
