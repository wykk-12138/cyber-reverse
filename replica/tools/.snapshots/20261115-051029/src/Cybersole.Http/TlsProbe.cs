using System.Diagnostics;
using System.Net.Security;
using System.Net.Sockets;
using System.Security.Authentication;
using System.Security.Cryptography.X509Certificates;

namespace Cybersole.Http;

public sealed record TlsProbeResult(
    string Host,
    string Protocol,
    string CipherSuite,
    string? Alpn,
    bool Ok,
    int HandshakeMs,
    string? Error);

/// <summary>
/// Diagnostics helper: performs a real TLS handshake with a <see cref="TlsProfile"/>
/// and reports the negotiated protocol / suite / ALPN. Used to verify that the
/// fingerprint settings actually reach the wire (and to compare profiles).
/// </summary>
public static class TlsProbe
{
    public static async Task<TlsProbeResult> ProbeAsync(string host, int port, TlsProfile profile,
        Cybersole.Core.Models.Proxy? proxy = null, CancellationToken ct = default)
    {
        var sw = Stopwatch.StartNew();
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

            await using var _ = transport.ConfigureAwait(false);
            using var ssl = new SslStream(transport, leaveInnerStreamOpen: false);
            var options = new SslClientAuthenticationOptions
            {
                TargetHost = host,
                EnabledSslProtocols = SslProtocols.Tls12 | SslProtocols.Tls13,
                ApplicationProtocols = profile.BuildAlpn(),
                CipherSuitesPolicy = profile.BuildCipherPolicy(),
                CertificateRevocationCheckMode = X509RevocationMode.NoCheck,
            };
            await ssl.AuthenticateAsClientAsync(options, ct).ConfigureAwait(false);
            sw.Stop();

            return new TlsProbeResult(
                host,
                ssl.SslProtocol.ToString(),
                ssl.NegotiatedCipherSuite.ToString(),
                ssl.NegotiatedApplicationProtocol.Protocol.IsEmpty
                    ? null
                    : System.Text.Encoding.ASCII.GetString(ssl.NegotiatedApplicationProtocol.Protocol.Span),
                Ok: true,
                (int)sw.ElapsedMilliseconds,
                Error: null);
        }
        catch (Exception ex)
        {
            sw.Stop();
            return new TlsProbeResult(host, "-", "-", null, false, (int)sw.ElapsedMilliseconds, ex.Message);
        }
    }

    /// <summary>Probe every profile against the same host (fingerprint comparison).</summary>
    public static async Task<IReadOnlyList<TlsProbeResult>> CompareAsync(string host, int port = 443,
        CancellationToken ct = default)
    {
        var results = new List<TlsProbeResult>();
        foreach (var profile in TlsProfile.All)
            results.Add(await ProbeAsync(host, port, profile, null, ct).ConfigureAwait(false));
        return results;
    }
}
